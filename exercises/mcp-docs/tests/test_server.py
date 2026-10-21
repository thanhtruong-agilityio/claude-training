import pytest

import mcp_server


@pytest.fixture(autouse=True)
def docs(monkeypatch):
    data = {
        "plan.md": "first migrate. then switch.",
        "spec.txt": "must respond within 200 ms.",
    }
    monkeypatch.setattr(mcp_server, "docs", data)
    return data


def test_read_returns_text():
    assert mcp_server.read_doc_contents("plan.md") == "first migrate. then switch."


def test_read_unknown_doc_raises():
    with pytest.raises(ValueError, match="nope.md"):
        mcp_server.read_doc_contents("nope.md")


def test_edit_replaces_text(docs):
    mcp_server.edit_document("plan.md", "first", "1st")
    assert docs["plan.md"] == "1st migrate. then switch."


def test_edit_unknown_doc_raises():
    with pytest.raises(ValueError, match="nope.md"):
        mcp_server.edit_document("nope.md", "a", "b")


def test_edit_missing_old_str_raises():
    with pytest.raises(ValueError, match="not found"):
        mcp_server.edit_document("plan.md", "absent text", "x")


def test_edit_match_is_exact_about_whitespace():
    with pytest.raises(ValueError, match="not found"):
        mcp_server.edit_document("plan.md", "first  migrate", "x")


def test_list_docs_returns_ids():
    assert mcp_server.list_docs() == ["plan.md", "spec.txt"]


def test_fetch_doc_returns_text():
    assert mcp_server.fetch_doc("spec.txt") == "must respond within 200 ms."


def test_fetch_unknown_doc_raises():
    with pytest.raises(ValueError, match="nope.md"):
        mcp_server.fetch_doc("nope.md")


def test_format_prompt_is_one_user_message_naming_the_doc():
    messages = mcp_server.format_document("plan.md")
    assert len(messages) == 1
    assert messages[0].role == "user"
    text = messages[0].content.text
    assert "plan.md" in text
    assert "edit_document" in text
    assert "markdown" in text.lower()
