import sys
from pathlib import Path

import pytest
from mcp.shared.exceptions import McpError

import mcp_server
from mcp_client import MCPClient

SERVER = Path(__file__).resolve().parent.parent / "mcp_server.py"


def make_client() -> MCPClient:
    return MCPClient(sys.executable, [str(SERVER)])


async def test_list_tools():
    async with make_client() as client:
        tools = await client.list_tools()
    assert {t.name for t in tools} == {"read_doc_contents", "edit_document"}
    assert all(t.inputSchema for t in tools)


async def test_call_tool_reads_doc():
    async with make_client() as client:
        result = await client.call_tool("read_doc_contents", {"doc_id": "plan.md"})
    assert not result.isError
    assert result.content[0].text == mcp_server.docs["plan.md"]


async def test_call_tool_unknown_doc_is_error_not_exception():
    async with make_client() as client:
        result = await client.call_tool("read_doc_contents", {"doc_id": "nope.md"})
    assert result.isError is True


async def test_edit_then_read_shares_server_state():
    async with make_client() as client:
        await client.call_tool(
            "edit_document",
            {"doc_id": "spec.txt", "old_str": "200 ms", "new_str": "100 ms"},
        )
        result = await client.call_tool("read_doc_contents", {"doc_id": "spec.txt"})
    assert "100 ms" in result.content[0].text


async def test_read_direct_resource_parses_json():
    async with make_client() as client:
        ids = await client.read_resource("docs://documents")
    assert ids == list(mcp_server.docs)


async def test_read_templated_resource_returns_text():
    async with make_client() as client:
        text = await client.read_resource("docs://documents/spec.txt")
    assert text == mcp_server.docs["spec.txt"]


async def test_read_unknown_resource_raises():
    async with make_client() as client:
        with pytest.raises(McpError):
            await client.read_resource("docs://documents/nope.md")


async def test_list_prompts():
    async with make_client() as client:
        prompts = await client.list_prompts()
    assert [p.name for p in prompts] == ["format"]
    assert [a.name for a in prompts[0].arguments] == ["doc_id"]


async def test_get_prompt_fills_in_argument():
    async with make_client() as client:
        messages = await client.get_prompt("format", {"doc_id": "plan.md"})
    assert messages[0].role == "user"
    assert "plan.md" in messages[0].content.text


async def test_get_unknown_prompt_raises():
    async with make_client() as client:
        with pytest.raises(McpError):
            await client.get_prompt("nope", {})
