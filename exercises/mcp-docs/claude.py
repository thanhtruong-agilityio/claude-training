from llm import Reply, ToolCall


def _to_anthropic(message: dict) -> dict:
    role = message["role"]
    if role == "user":
        return {"role": "user", "content": message["content"]}
    if role == "assistant":
        blocks = []
        if message["text"]:
            blocks.append({"type": "text", "text": message["text"]})
        for call in message["tool_calls"]:
            blocks.append(
                {"type": "tool_use", "id": call.id, "name": call.name, "input": call.input}
            )
        return {"role": "assistant", "content": blocks}
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": r["id"],
                "content": r["content"],
                "is_error": r["is_error"],
            }
            for r in message["results"]
        ],
    }


class Claude:
    def __init__(self, client, model: str, max_tokens: int = 8000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    async def chat(self, messages: list[dict], tools: list[dict]) -> Reply:
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [_to_anthropic(m) for m in messages],
        }
        if tools:
            params["tools"] = tools
        response = await self.client.messages.create(**params)
        text = "".join(b.text for b in response.content if b.type == "text")
        calls = [
            ToolCall(b.id, b.name, b.input)
            for b in response.content
            if b.type == "tool_use"
        ]
        return Reply(text=text, tool_calls=calls)
