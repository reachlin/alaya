"""Anthropic adapter. One round of the sixth consciousness per call."""
from __future__ import annotations

import os

from alaya.providers.base import Call, Provider, Response, ToolSpec


class ClaudeProvider(Provider):
    name = "claude"

    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 1024):
        import anthropic

        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def converse(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> Response:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=_to_anthropic(messages),
            tools=[{"name": t.name, "description": t.description, "input_schema": t.schema}
                   for t in tools],
        )
        text = "".join(b.text for b in response.content if b.type == "text") or None
        calls = [Call(name=b.name, args=dict(b.input), id=b.id)
                 for b in response.content if b.type == "tool_use"]
        return Response(text=text, calls=calls)


def _to_anthropic(messages: list[dict]) -> list[dict]:
    """Flatten the internal transcript into alternating user/assistant turns.

    Tool results are folded into the user turn rather than modelled as separate
    blocks: the loop here is short (a handful of rounds inside one 刹那), and
    keeping the wire format simple keeps the doctrine-bearing code readable.
    """
    out: list[dict] = []
    for m in messages:
        if m["role"] == "user":
            out.append({"role": "user", "content": m["content"]})
        elif m["role"] == "assistant":
            called = ", ".join(m.get("calls", ()))
            out.append({"role": "assistant",
                        "content": m.get("content") or f"(calling {called})"})
        elif m["role"] == "tool":
            out.append({"role": "user", "content": f"[result] {m['content']}"})
    return out
