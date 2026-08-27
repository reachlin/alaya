"""Model adapters for the sixth consciousness."""
from alaya.providers.base import Call, Provider, Response, ToolSpec
from alaya.providers.echo import EchoProvider

__all__ = ["Call", "EchoProvider", "Provider", "Response", "ToolSpec", "build"]


def build(name: str = "echo", model: str | None = None) -> Provider:
    """Resolve a provider by name, importing its SDK only when actually asked."""
    if name == "echo":
        return EchoProvider()
    if name == "claude":
        from alaya.providers.claude import ClaudeProvider

        return ClaudeProvider(model=model or "claude-sonnet-5")
    if name == "openai":
        from alaya.providers.openai import OpenAIProvider

        return OpenAIProvider(model=model or "gpt-4o")
    raise ValueError(f"unknown provider {name!r} (echo, claude, openai)")
