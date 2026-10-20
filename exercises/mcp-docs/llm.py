"""Provider-neutral types shared by the chat loop and the LLM adapters.

History entries (`messages`) are plain dicts:
  {"role": "user", "content": str}
  {"role": "assistant", "text": str, "tool_calls": list[ToolCall]}
  {"role": "tool_results", "results": [{"id": str, "content": str, "is_error": bool}]}

Tools are dicts: {"name": str, "description": str, "input_schema": dict}.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class Reply:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
