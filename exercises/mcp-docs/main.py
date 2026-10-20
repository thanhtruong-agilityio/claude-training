import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from chat import Chat
from cli import run_cli
from mcp_client import MCPClient
from providers import make_llm

HERE = Path(__file__).resolve().parent


async def main() -> None:
    load_dotenv(HERE / ".env")
    llm = make_llm(os.environ)
    async with MCPClient(sys.executable, [str(HERE / "mcp_server.py")]) as client:
        await run_cli(Chat(llm, client))


if __name__ == "__main__":
    asyncio.run(main())
