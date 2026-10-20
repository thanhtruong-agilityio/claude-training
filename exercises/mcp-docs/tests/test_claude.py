from types import SimpleNamespace as NS

from claude import Claude
from llm import ToolCall

TOOLS = [{"name": "t", "description": "d", "input_schema": {"type": "object"}}]


class FakeMessages:
    def __init__(self, reply):
        self.reply = reply
        self.params = None

    async def create(self, **params):
        self.params = params
        return self.reply


def make(*blocks):
    messages = FakeMessages(NS(content=list(blocks)))
    return Claude(NS(messages=messages), "test-model", max_tokens=50), messages


def text_block(text):
    return NS(type="text", text=text)


def tool_block(tool_id, name, tool_input):
    return NS(type="tool_use", id=tool_id, name=name, input=tool_input)


async def test_passes_params_and_returns_text():
    claude, messages = make(text_block("hi"))
    reply = await claude.chat([{"role": "user", "content": "q"}], TOOLS)
    assert messages.params == {
        "model": "test-model",
        "max_tokens": 50,
        "messages": [{"role": "user", "content": "q"}],
        "tools": TOOLS,
    }
    assert reply.text == "hi"
    assert reply.tool_calls == []


async def test_omits_tools_when_empty():
    claude, messages = make(text_block("hi"))
    await claude.chat([{"role": "user", "content": "q"}], [])
    assert "tools" not in messages.params


async def test_tool_use_blocks_become_tool_calls():
    claude, _ = make(
        text_block("looking"),
        tool_block("t1", "read_doc_contents", {"doc_id": "plan.md"}),
    )
    reply = await claude.chat([{"role": "user", "content": "q"}], TOOLS)
    assert reply.text == "looking"
    assert reply.tool_calls == [ToolCall("t1", "read_doc_contents", {"doc_id": "plan.md"})]


async def test_history_is_converted_to_anthropic_format():
    claude, messages = make(text_block("ok"))
    history = [
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "text": "let me look",
            "tool_calls": [ToolCall("t1", "read_doc_contents", {"doc_id": "plan.md"})],
        },
        {
            "role": "tool_results",
            "results": [{"id": "t1", "content": "body", "is_error": False}],
        },
    ]
    await claude.chat(history, TOOLS)
    assert messages.params["messages"] == [
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "let me look"},
                {
                    "type": "tool_use",
                    "id": "t1",
                    "name": "read_doc_contents",
                    "input": {"doc_id": "plan.md"},
                },
            ],
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "t1",
                    "content": "body",
                    "is_error": False,
                }
            ],
        },
    ]


async def test_empty_assistant_text_is_not_sent_as_a_block():
    claude, messages = make(text_block("ok"))
    history = [
        {"role": "user", "content": "q"},
        {"role": "assistant", "text": "", "tool_calls": [ToolCall("t1", "x", {})]},
    ]
    await claude.chat(history, TOOLS)
    blocks = messages.params["messages"][1]["content"]
    assert [b["type"] for b in blocks] == ["tool_use"]
