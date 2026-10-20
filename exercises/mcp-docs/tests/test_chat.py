import sys
from pathlib import Path
import pytest

import mcp_server
from chat import Chat, ChatInputError
from llm import Reply, ToolCall
from mcp_client import MCPClient

SERVER = Path(__file__).resolve().parent.parent / "mcp_server.py"


class StubLLM:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    async def chat(self, messages, tools=None):
        self.calls.append({"messages": [*messages], "tools": tools})
        return self.replies.pop(0)


def text_reply(text):
    return Reply(text=text, tool_calls=[])


def tool_reply(name, tool_input, tool_id="t1"):
    return Reply(text="", tool_calls=[ToolCall(tool_id, name, tool_input)])


def make_client():
    return MCPClient(sys.executable, [str(SERVER)])


async def test_plain_question_sends_tools_and_returns_text():
    claude = StubLLM([text_reply("hello")])
    async with make_client() as client:
        answer = await Chat(claude, client).run("hi")
    assert answer == "hello"
    names = {t["name"] for t in claude.calls[0]["tools"]}
    assert names == {"read_doc_contents", "edit_document"}
    assert all("input_schema" in t for t in claude.calls[0]["tools"])


async def test_tool_loop_runs_tool_and_returns_final_text():
    claude = StubLLM(
        [
            tool_reply("read_doc_contents", {"doc_id": "plan.md"}),
            text_reply("it says migrate"),
        ]
    )
    async with make_client() as client:
        answer = await Chat(claude, client).run("what does plan.md say?")
    assert answer == "it says migrate"
    last = claude.calls[1]["messages"][-1]
    assert last["role"] == "tool_results"
    result = last["results"][0]
    assert result["id"] == "t1"
    assert result["content"] == mcp_server.docs["plan.md"]
    assert result["is_error"] is False


async def test_tool_error_is_sent_back_as_is_error():
    claude = StubLLM(
        [
            tool_reply("read_doc_contents", {"doc_id": "nope.md"}),
            text_reply("that doc does not exist"),
        ]
    )
    async with make_client() as client:
        answer = await Chat(claude, client).run("read nope.md")
    assert answer == "that doc does not exist"
    result = claude.calls[1]["messages"][-1]["results"][0]
    assert result["is_error"] is True
    assert "nope.md" in result["content"]


async def test_mention_injects_document_content():
    claude = StubLLM([text_reply("ok")])
    async with make_client() as client:
        await Chat(claude, client).run("summarize @plan.md.")
    content = claude.calls[0]["messages"][0]["content"]
    assert "summarize @plan.md." in content
    assert '<document id="plan.md">' in content
    assert mcp_server.docs["plan.md"] in content


async def test_unknown_mention_raises_and_skips_claude():
    claude = StubLLM([])
    async with make_client() as client:
        chat = Chat(claude, client)
        with pytest.raises(ChatInputError, match="nope.md"):
            await chat.run("read @nope.md")
    assert claude.calls == []
    assert chat.messages == []


async def test_command_sends_server_prompt_messages():
    claude = StubLLM([text_reply("formatted")])
    async with make_client() as client:
        answer = await Chat(claude, client).run("/format plan.md")
    assert answer == "formatted"
    first = claude.calls[0]["messages"][0]
    assert first["role"] == "user"
    assert "plan.md" in first["content"]
    assert "edit_document" in first["content"]


async def test_unknown_command_raises():
    claude = StubLLM([])
    async with make_client() as client:
        with pytest.raises(ChatInputError, match="/nope"):
            await Chat(claude, client).run("/nope plan.md")
    assert claude.calls == []


async def test_command_with_wrong_arg_count_raises_with_usage():
    claude = StubLLM([])
    async with make_client() as client:
        with pytest.raises(ChatInputError, match="/format <doc_id>"):
            await Chat(claude, client).run("/format")
    assert claude.calls == []


async def test_history_persists_across_runs():
    claude = StubLLM([text_reply("one"), text_reply("two")])
    async with make_client() as client:
        chat = Chat(claude, client)
        await chat.run("first")
        await chat.run("second")
    roles = [m["role"] for m in claude.calls[1]["messages"]]
    assert roles == ["user", "assistant", "user"]


async def test_doc_ids_and_command_names():
    async with make_client() as client:
        chat = Chat(StubLLM([]), client)
        assert await chat.doc_ids() == list(mcp_server.docs)
        assert await chat.command_names() == ["format"]
