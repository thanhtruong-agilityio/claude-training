import re

from mcp_client import MCPClient

# Doc ids look like "plan.md"; a trailing period ends a sentence, not the id.
MENTION = re.compile(r"@([\w-]+(?:\.[\w-]+)*)")


class ChatInputError(Exception):
    """Bad user input. The message is meant to be shown to the user."""


def _result_text(result) -> str:
    return "".join(c.text for c in result.content if c.type == "text")


def _reply_text(reply) -> str:
    return "".join(b.text for b in reply.content if b.type == "text")


class Chat:
    def __init__(self, claude, client: MCPClient):
        self.claude = claude
        self.client = client
        self.messages: list[dict] = []

    async def doc_ids(self) -> list[str]:
        return await self.client.read_resource("docs://documents")

    async def command_names(self) -> list[str]:
        return [p.name for p in await self.client.list_prompts()]

    async def run(self, query: str) -> str:
        # Build the new messages first: bad input must not touch the history.
        if query.startswith("/"):
            new_messages = await self._command_messages(query)
        else:
            new_messages = [await self._mention_message(query)]
        self.messages.extend(new_messages)

        tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in await self.client.list_tools()
        ]

        while True:
            reply = await self.claude.chat(self.messages, tools)
            self.messages.append({"role": "assistant", "content": reply.content})
            if reply.stop_reason != "tool_use":
                return _reply_text(reply)

            results = []
            for block in reply.content:
                if block.type != "tool_use":
                    continue
                result = await self.client.call_tool(block.name, block.input)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": _result_text(result),
                        "is_error": bool(result.isError),
                    }
                )
            self.messages.append({"role": "user", "content": results})

    async def _mention_message(self, query: str) -> dict:
        mentioned = list(dict.fromkeys(MENTION.findall(query)))
        known = await self.doc_ids()
        for doc_id in mentioned:
            if doc_id not in known:
                raise ChatInputError(f"Unknown document: {doc_id}")
        content = query
        for doc_id in mentioned:
            text = await self.client.read_resource(f"docs://documents/{doc_id}")
            content += f'\n\n<document id="{doc_id}">\n{text}\n</document>'
        return {"role": "user", "content": content}

    async def _command_messages(self, query: str) -> list[dict]:
        name, *args = query[1:].split()
        prompts = {p.name: p for p in await self.client.list_prompts()}
        if name not in prompts:
            raise ChatInputError(f"Unknown command: /{name}")
        arg_names = [a.name for a in (prompts[name].arguments or [])]
        if len(args) != len(arg_names):
            usage = " ".join(f"<{a}>" for a in arg_names)
            raise ChatInputError(f"Usage: /{name} {usage}")
        messages = await self.client.get_prompt(name, dict(zip(arg_names, args)))
        return [{"role": m.role, "content": m.content.text} for m in messages]
