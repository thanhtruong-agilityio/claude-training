from prompt_toolkit.document import Document

from cli import CliCompleter


def complete(text: str) -> list[str]:
    completer = CliCompleter(["plan.md", "spec.txt"], ["format"])
    return [c.text for c in completer.get_completions(Document(text), None)]


def test_at_completes_doc_ids():
    assert complete("read @pl") == ["plan.md"]


def test_slash_completes_commands():
    assert complete("/for") == ["format"]


def test_word_after_command_completes_doc_ids():
    assert complete("/format sp") == ["spec.txt"]


def test_plain_text_completes_nothing():
    assert complete("hello") == []
