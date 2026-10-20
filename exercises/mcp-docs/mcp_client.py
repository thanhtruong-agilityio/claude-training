import json
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self._params = StdioServerParameters(command=command, args=args)
        self._stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def connect(self) -> None:
        read, write = await self._stack.enter_async_context(stdio_client(self._params))
        self._session = await self._stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()

    async def cleanup(self) -> None:
        await self._stack.aclose()
        self._session = None

    async def __aenter__(self) -> "MCPClient":
        try:
            await self.connect()
        except BaseException:
            await self.cleanup()
            raise
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self.cleanup()

    def _require_session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("MCPClient is not connected")
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        result = await self._require_session().list_tools()
        return result.tools

    async def call_tool(self, name: str, input: dict) -> types.CallToolResult:
        return await self._require_session().call_tool(name, input)

    async def read_resource(self, uri: str) -> Any:
        result = await self._require_session().read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text
        raise ValueError(f"Resource {uri} is not text")

    async def list_prompts(self) -> list[types.Prompt]:
        result = await self._require_session().list_prompts()
        return result.prompts

    async def get_prompt(
        self, name: str, args: dict[str, str]
    ) -> list[types.PromptMessage]:
        result = await self._require_session().get_prompt(name, args)
        return result.messages
