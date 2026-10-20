import json

from llm import Reply, ToolCall


def _to_openai_messages(messages: list[dict]) -> list[dict]:
    converted = []
    for message in messages:
        role = message["role"]
        if role == "user":
            converted.append({"role": "user", "content": message["content"]})
        elif role == "assistant":
            entry = {"role": "assistant", "content": message["text"] or None}
            if message["tool_calls"]:
                entry["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.input),
                        },
                    }
                    for call in message["tool_calls"]
                ]
            converted.append(entry)
        else:
            # OpenAI has no is_error flag: carry the error in the content.
            for result in message["results"]:
                content = result["content"]
                if result["is_error"]:
                    content = f"Error: {content}"
                converted.append(
                    {"role": "tool", "tool_call_id": result["id"], "content": content}
                )
    return converted


def _parse_arguments(arguments: str | None) -> dict:
    # A malformed argument string becomes {}: the tool then reports the missing
    # arguments and the model can correct itself.
    try:
        parsed = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


class OpenAILLM:
    def __init__(self, client, model: str):
        self.client = client
        self.model = model

    async def chat(self, messages: list[dict], tools: list[dict]) -> Reply:
        params = {"model": self.model, "messages": _to_openai_messages(messages)}
        if tools:
            params["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"],
                    },
                }
                for t in tools
            ]
        response = await self.client.chat.completions.create(**params)
        message = response.choices[0].message
        calls = [
            ToolCall(c.id, c.function.name, _parse_arguments(c.function.arguments))
            for c in (message.tool_calls or [])
        ]
        return Reply(text=message.content or "", tool_calls=calls)
