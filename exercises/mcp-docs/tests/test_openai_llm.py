import json
from types import SimpleNamespace as NS

from llm import ToolCall
from openai_llm import OpenAILLM

TOOLS = [
    {
        "name": "read_doc_contents",
        "description": "Read a doc",
        "input_schema": {"type": "object", "properties": {"doc_id": {"type": "string"}}},
    }
]


class FakeCompletions:
    def __init__(self, message):
        self.message = message
        self.params = None

    async def create(self, **params):
        self.params = params
        return NS(choices=[NS(message=self.message)])


def make(content=None, tool_calls=None):
    completions = FakeCompletions(NS(content=content, tool_calls=tool_calls))
    client = NS(chat=NS(completions=completions))
    return OpenAILLM(client, "test-model"), completions


def call(call_id, name, arguments):
    return NS(id=call_id, function=NS(name=name, arguments=arguments))


async def test_passes_model_messages_and_openai_style_tools():
    llm, completions = make(content="hi")
    reply = await llm.chat([{"role": "user", "content": "q"}], TOOLS)
    assert completions.params == {
        "model": "test-model",
        "messages": [{"role": "user", "content": "q"}],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "read_doc_contents",
                    "description": "Read a doc",
                    "parameters": TOOLS[0]["input_schema"],
                },
            }
        ],
    }
    assert reply.text == "hi"
    assert reply.tool_calls == []


async def test_omits_tools_when_empty():
    llm, completions = make(content="hi")
    await llm.chat([{"role": "user", "content": "q"}], [])
    assert "tools" not in completions.params


async def test_tool_call_arguments_are_parsed_from_json():
    llm, _ = make(
        content=None,
        tool_calls=[call("c1", "read_doc_contents", '{"doc_id": "plan.md"}')],
    )
    reply = await llm.chat([{"role": "user", "content": "q"}], TOOLS)
    assert reply.text == ""
    assert reply.tool_calls == [ToolCall("c1", "read_doc_contents", {"doc_id": "plan.md"})]


async def test_unparseable_arguments_become_empty_input():
    llm, _ = make(tool_calls=[call("c1", "read_doc_contents", "{not json")])
    reply = await llm.chat([{"role": "user", "content": "q"}], TOOLS)
    assert reply.tool_calls == [ToolCall("c1", "read_doc_contents", {})]


async def test_history_is_converted_to_openai_format():
    llm, completions = make(content="ok")
    tool_input = {"doc_id": "plan.md"}
    history = [
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "text": "let me look",
            "tool_calls": [ToolCall("c1", "read_doc_contents", tool_input)],
        },
        {
            "role": "tool_results",
            "results": [
                {"id": "c1", "content": "body", "is_error": False},
                {"id": "c2", "content": "Doc not found", "is_error": True},
            ],
        },
    ]
    await llm.chat(history, TOOLS)
    assert completions.params["messages"] == [
        {"role": "user", "content": "q"},
        {
            "role": "assistant",
            "content": "let me look",
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {
                        "name": "read_doc_contents",
                        "arguments": json.dumps(tool_input),
                    },
                }
            ],
        },
        {"role": "tool", "tool_call_id": "c1", "content": "body"},
        {"role": "tool", "tool_call_id": "c2", "content": "Error: Doc not found"},
    ]


async def test_assistant_without_tool_calls_omits_the_key():
    llm, completions = make(content="ok")
    history = [
        {"role": "user", "content": "q"},
        {"role": "assistant", "text": "answer", "tool_calls": []},
        {"role": "user", "content": "next"},
    ]
    await llm.chat(history, [])
    assert completions.params["messages"][1] == {"role": "assistant", "content": "answer"}
