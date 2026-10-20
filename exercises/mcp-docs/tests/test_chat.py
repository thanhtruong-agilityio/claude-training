import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

import mcp_server
from chat import Chat, ChatInputError
from mcp_client import MCPClient

SERVER = Path(__file__).resolve().parent.parent / "mcp_server.py"


class StubClaude:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    async def chat(self, messages, tools=None):
        self.calls.append({"messages": [*messages], "tools": tools})
        return self.replies.pop(0)


def text_reply(text):
    return NS(stop_reason="end_turn", content=[NS(type="text", text=text)])


def tool_reply(name, tool_input, tool_id="t1"):
    return NS(
        stop_reason="tool_use",
        content=[NS(type="tool_use", id=tool_id, name=name, input=tool_input)],
    )


def make_client():
    return MCPClient(sys.executable, [str(SERVER)])


async def test_plain_question_sends_tools_and_returns_text():
    claude = StubClaude([text_reply("hello")])
    async with make_client() as client:
        answer = await Chat(claude, client).run("hi")
    assert answer == "hello"
    names = {t["name"] for t in claude.calls[0]["tools"]}
    assert names == {"read_doc_contents", "edit_document"}
    assert all("input_schema" in t for t in claude.calls[0]["tools"])


async def test_tool_loop_runs_tool_and_returns_final_text():
    claude = StubClaude(
        [
            tool_reply("read_doc_contents", {"doc_id": "plan.md"}),
            text_reply("it says migrate"),
        ]
    )
    async with make_client() as client:
        answer = await Chat(claude, client).run("what does plan.md say?")
    assert answer == "it says migrate"
    last = claude.calls[1]["messages"][-1]
    assert last["role"] == "user"
    block = last["content"][0]
    assert block["type"] == "tool_result"
    assert block["tool_use_id"] == "t1"
    assert block["content"] == mcp_server.docs["plan.md"]
    assert block["is_error"] is False


async def test_tool_error_is_sent_back_as_is_error():
    claude = StubClaude(
        [
            tool_reply("read_doc_contents", {"doc_id": "nope.md"}),
            text_reply("that doc does not exist"),
        ]
    )
    async with make_client() as client:
        answer = await Chat(claude, client).run("read nope.md")
    assert answer == "that doc does not exist"
    block = claude.calls[1]["messages"][-1]["content"][0]
    assert block["is_error"] is True
    assert "nope.md" in block["content"]


async def test_mention_injects_document_content():
    claude = StubClaude([text_reply("ok")])
    async with make_client() as client:
        await Chat(claude, client).run("summarize @plan.md.")
    content = claude.calls[0]["messages"][0]["content"]
    assert "summarize @plan.md." in content
    assert '<document id="plan.md">' in content
    assert mcp_server.docs["plan.md"] in content


async def test_unknown_mention_raises_and_skips_claude():
    claude = StubClaude([])
    async with make_client() as client:
        chat = Chat(claude, client)
        with pytest.raises(ChatInputError, match="nope.md"):
            await chat.run("read @nope.md")
    assert claude.calls == []
    assert chat.messages == []


async def test_command_sends_server_prompt_messages():
    claude = StubClaude([text_reply("formatted")])
    async with make_client() as client:
        answer = await Chat(claude, client).run("/format plan.md")
    assert answer == "formatted"
    first = claude.calls[0]["messages"][0]
    assert first["role"] == "user"
    assert "plan.md" in first["content"]
    assert "edit_document" in first["content"]


async def test_unknown_command_raises():
    claude = StubClaude([])
    async with make_client() as client:
        with pytest.raises(ChatInputError, match="/nope"):
            await Chat(claude, client).run("/nope plan.md")
    assert claude.calls == []


async def test_command_with_wrong_arg_count_raises_with_usage():
    claude = StubClaude([])
    async with make_client() as client:
        with pytest.raises(ChatInputError, match="/format <doc_id>"):
            await Chat(claude, client).run("/format")
    assert claude.calls == []


async def test_history_persists_across_runs():
    claude = StubClaude([text_reply("one"), text_reply("two")])
    async with make_client() as client:
        chat = Chat(claude, client)
        await chat.run("first")
        await chat.run("second")
    roles = [m["role"] for m in claude.calls[1]["messages"]]
    assert roles == ["user", "assistant", "user"]


async def test_doc_ids_and_command_names():
    async with make_client() as client:
        chat = Chat(StubClaude([]), client)
        assert await chat.doc_ids() == list(mcp_server.docs)
        assert await chat.command_names() == ["format"]
