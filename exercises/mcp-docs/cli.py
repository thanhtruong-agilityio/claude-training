import anthropic
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

from chat import Chat, ChatInputError


class CliCompleter(Completer):
    def __init__(self, doc_ids: list[str], commands: list[str]):
        self.doc_ids = doc_ids
        self.commands = commands

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)

        if word.startswith("@"):
            yield from self._matches(word[1:], self.doc_ids)
        elif text.startswith("/") and " " not in text:
            yield from self._matches(word[1:], self.commands)
        elif text.startswith("/"):
            yield from self._matches(word, self.doc_ids)

    @staticmethod
    def _matches(prefix: str, options: list[str]):
        for option in options:
            if option.startswith(prefix):
                yield Completion(option, start_position=-len(prefix))


async def run_cli(chat: Chat) -> None:
    session = PromptSession(
        completer=CliCompleter(await chat.doc_ids(), await chat.command_names()),
        complete_while_typing=True,
    )
    print("Ask a question. @doc adds a document, /format <doc> runs a prompt. Ctrl-D quits.")
    while True:
        try:
            query = (await session.prompt_async("> ")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not query:
            continue
        try:
            print(await chat.run(query))
        except ChatInputError as error:
            print(error)
        except anthropic.APIError as error:
            print(f"Claude API error: {error}")
