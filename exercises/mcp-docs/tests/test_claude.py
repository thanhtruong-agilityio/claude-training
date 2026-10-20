from types import SimpleNamespace

from claude import Claude


class FakeMessages:
    def __init__(self):
        self.params = None

    async def create(self, **params):
        self.params = params
        return "reply"


def make():
    messages = FakeMessages()
    return Claude(SimpleNamespace(messages=messages), "test-model", max_tokens=50), messages


async def test_chat_passes_params_and_returns_reply():
    claude, messages = make()
    tools = [{"name": "t", "description": "d", "input_schema": {"type": "object"}}]
    reply = await claude.chat([{"role": "user", "content": "hi"}], tools)
    assert reply == "reply"
    assert messages.params == {
        "model": "test-model",
        "max_tokens": 50,
        "messages": [{"role": "user", "content": "hi"}],
        "tools": tools,
    }


async def test_chat_omits_tools_when_none():
    claude, messages = make()
    await claude.chat([{"role": "user", "content": "hi"}])
    assert "tools" not in messages.params
