from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from claude import Claude
from openai_llm import OpenAILLM

DEFAULT_CLAUDE_MODEL = "claude-sonnet-5-5"


def _require(env, name: str) -> str:
    value = env.get(name)
    if not value:
        raise SystemExit(f"{name} is not set (export it or put it in exercises/mcp-docs/.env)")
    return value


def make_llm(env):
    provider = (env.get("LLM_PROVIDER") or "anthropic").lower()
    if provider == "anthropic":
        key = _require(env, "ANTHROPIC_API_KEY")
        model = env.get("CLAUDE_MODEL") or DEFAULT_CLAUDE_MODEL
        return Claude(AsyncAnthropic(api_key=key), model)
    if provider == "openai":
        key = _require(env, "OPENAI_API_KEY")
        model = _require(env, "OPENAI_MODEL")
        return OpenAILLM(AsyncOpenAI(api_key=key), model)
    raise SystemExit(f"Unknown LLM_PROVIDER {provider!r} (use 'anthropic' or 'openai')")
