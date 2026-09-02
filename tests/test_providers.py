"""Choosing a sixth consciousness.

Nothing doctrinal here. Providers are the adapter between :mod:`alaya.mano` and
whatever model is available, and this file exists so the doctrine-bearing code
never has to know about API shapes or endpoints.

One thing does matter beyond plumbing: ``deliberative``. A stub with no model
behind it must never be handed a judgement call — 平等性智 asking for a
corrective, or ModelExaminer judging implication — because a stub does not fail
loudly, it answers with filler, and filler in the self-model is carried into
every subsequent prompt by 恆審思量.
"""
import importlib.util

import pytest

from alaya.providers import EchoProvider, MissingKey, build

#: Resolving an endpoint means constructing the SDK client. That is the only
#: part of these tests needing the SDK — everything about *which* endpoint,
#: model and key variable is ours, and is checked below.
needs_sdk = pytest.mark.skipif(
    importlib.util.find_spec("openai") is None,
    reason="openai SDK not installed; install with .[providers]",
)


def test_the_echo_provider_is_the_default():
    assert build().name == "echo"
    assert isinstance(build(), EchoProvider)


def test_a_stub_is_never_deliberative():
    assert build().deliberative is False


@needs_sdk
def test_deepseek_points_at_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    provider = build("deepseek")
    assert "api.deepseek.com" in str(provider.base_url)
    assert provider.model == "deepseek-chat"
    assert provider.deliberative is True


@needs_sdk
def test_deepseek_takes_a_model_override(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    assert build("deepseek", "deepseek-reasoner").model == "deepseek-reasoner"


@needs_sdk
def test_ollama_needs_no_key_at_all(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = build("ollama")
    assert "11434" in str(provider.base_url)
    assert provider.model


@needs_sdk
def test_an_explicit_base_url_wins(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    provider = build("openai", base_url="http://elsewhere:8000/v1")
    assert "elsewhere:8000" in str(provider.base_url)


def test_a_missing_key_says_which_variable_to_set(monkeypatch):
    """A cryptic SDK error here costs someone twenty minutes. Name the variable."""
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(MissingKey) as exc:
        build("deepseek")
    assert "DEEPSEEK_API_KEY" in str(exc.value)


def test_an_unknown_provider_lists_the_known_ones():
    with pytest.raises(ValueError) as exc:
        build("hal9000")
    for name in ("echo", "claude", "openai", "deepseek", "ollama"):
        assert name in str(exc.value)
