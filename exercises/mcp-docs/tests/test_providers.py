import pytest

from claude import Claude
from openai_llm import OpenAILLM
from providers import make_llm


def test_default_provider_is_anthropic():
    llm = make_llm({"ANTHROPIC_API_KEY": "k"})
    assert isinstance(llm, Claude)
    assert llm.model == "claude-sonnet-5-5"


def test_claude_model_can_be_overridden():
    llm = make_llm({"ANTHROPIC_API_KEY": "k", "CLAUDE_MODEL": "other-model"})
    assert llm.model == "other-model"


def test_anthropic_missing_key_names_the_variable():
    with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY"):
        make_llm({})


def test_openai_provider():
    env = {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "k", "OPENAI_MODEL": "m"}
    llm = make_llm(env)
    assert isinstance(llm, OpenAILLM)
    assert llm.model == "m"


def test_openai_missing_key_names_the_variable():
    with pytest.raises(SystemExit, match="OPENAI_API_KEY"):
        make_llm({"LLM_PROVIDER": "openai", "OPENAI_MODEL": "m"})


def test_openai_missing_model_names_the_variable():
    with pytest.raises(SystemExit, match="OPENAI_MODEL"):
        make_llm({"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "k"})


def test_unknown_provider_names_the_variable():
    with pytest.raises(SystemExit, match="LLM_PROVIDER"):
        make_llm({"LLM_PROVIDER": "nope"})
