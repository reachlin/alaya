"""Model adapters for the sixth consciousness.

    echo      no model at all — the whole system runs offline on this
    claude    Anthropic
    openai    OpenAI, or anything OpenAI-compatible via --base-url
    deepseek  DeepSeek (OpenAI-compatible)
    ollama    a local model, no key and no network

Only ``echo`` is a dependency-free default. Every other adapter imports its SDK
lazily, so the package installs and the tests run without any of them.
"""
import os

from alaya.providers.base import Call, Provider, Response, ToolSpec
from alaya.providers.echo import EchoProvider

__all__ = ["Call", "EchoProvider", "MissingKey", "Provider", "Response",
           "ToolSpec", "build", "ENDPOINTS"]


class MissingKey(RuntimeError):
    """No credential for the chosen provider — naming the variable to set."""


#: OpenAI-compatible endpoints. model, base_url, key variable.
ENDPOINTS = {
    "openai":   ("gpt-4o",        None,                             "OPENAI_API_KEY"),
    "deepseek": ("deepseek-chat", "https://api.deepseek.com/v1",    "DEEPSEEK_API_KEY"),
    # Local inference. No key, no network, nothing leaves the machine.
    "ollama":   ("qwen2.5:7b",    "http://localhost:11434/v1",      None),
}


def build(
    name: str = "echo",
    model: str | None = None,
    base_url: str | None = None,
) -> Provider:
    """Resolve a provider by name, importing its SDK only when actually asked."""
    if name == "echo":
        return EchoProvider()

    if name == "claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise MissingKey("set ANTHROPIC_API_KEY to use --provider claude")
        from alaya.providers.claude import ClaudeProvider

        return ClaudeProvider(model=model or "claude-sonnet-5")

    if name in ENDPOINTS:
        default_model, endpoint, key_env = ENDPOINTS[name]
        if key_env and not os.environ.get(key_env):
            raise MissingKey(
                f"set {key_env} to use --provider {name} — export it, or put it in a "
                f".env file and pass --env <path>"
            )
        from alaya.providers.openai import OpenAIProvider

        provider = OpenAIProvider(
            model=model or default_model,
            base_url=base_url or endpoint,
            api_key_env=key_env,
        )
        provider.name = name
        return provider

    known = ", ".join(["echo", "claude", *ENDPOINTS])
    raise ValueError(f"unknown provider {name!r} — known: {known}")
