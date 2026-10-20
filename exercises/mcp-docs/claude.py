class Claude:
    def __init__(self, client, model: str, max_tokens: int = 8000):
        self.client = client
        self.model = model
        self.max_tokens = max_tokens

    async def chat(self, messages: list[dict], tools: list[dict] | None = None):
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if tools:
            params["tools"] = tools
        return await self.client.messages.create(**params)
