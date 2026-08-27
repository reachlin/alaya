"""OpenAI adapter. Also serves any OpenAI-compatible endpoint (Ollama, vLLM)."""
from __future__ import annotations

import json
import os

from alaya.providers.base import Call, Provider, Response, ToolSpec


class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o", base_url: str | None = None):
        from openai import OpenAI

        self.model = model
        self._client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", "none"),
            base_url=base_url or os.environ.get("ALAYA_BASE_URL") or None,
        )

    def converse(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> Response:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, *_to_openai(messages)],
            tools=[{"type": "function",
                    "function": {"name": t.name, "description": t.description,
                                 "parameters": t.schema}}
                   for t in tools],
            max_tokens=1024,
        )
        message = response.choices[0].message
        calls = [
            Call(name=tc.function.name,
                 args=json.loads(tc.function.arguments or "{}"),
                 id=tc.id)
            for tc in (message.tool_calls or [])
        ]
        return Response(text=message.content, calls=calls)


def _to_openai(messages: list[dict]) -> list[dict]:
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
