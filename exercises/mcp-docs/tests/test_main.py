import pytest

from main import require_api_key


def test_missing_key_exits_naming_the_variable():
    with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY"):
        require_api_key({})


def test_returns_key_when_set():
    assert require_api_key({"ANTHROPIC_API_KEY": "k"}) == "k"
