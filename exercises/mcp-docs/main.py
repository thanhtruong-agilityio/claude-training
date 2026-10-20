import asyncio
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from chat import Chat
from claude import Claude
from cli import run_cli
from mcp_client import MCPClient

HERE = Path(__file__).resolve().parent
DEFAULT_MODEL = "claude-sonnet-5-5"


def require_api_key(env=os.environ) -> str:
    key = env.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit(
            "ANTHROPIC_API_KEY is not set (export it or put it in exercises/mcp-docs/.env)"
        )
    return key


async def main() -> None:
    load_dotenv(HERE / ".env")
    require_api_key()
    claude = Claude(AsyncAnthropic(), os.getenv("CLAUDE_MODEL") or DEFAULT_MODEL)
    async with MCPClient(sys.executable, [str(HERE / "mcp_server.py")]) as client:
        await run_cli(Chat(claude, client))


if __name__ == "__main__":
    asyncio.run(main())
