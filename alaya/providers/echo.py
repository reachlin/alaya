"""An offline provider, so the whole system runs with no API key.

It is also the clearest demonstration of why 三量 is worth recording. The echo
provider has *no* vision and *no* language model. All it sees is a line like

    · [eye] frame 1280×720 · luminance 0.42 · motion 0.11

and when it "remembers" something about that, it is doing exactly what the
sixth consciousness does: laying a name over a signal. Whether that name is
warranted is not something it can know about itself — which is the entire
reason the measure is computed from provenance in :mod:`alaya.mano` rather than
asserted by the model.
"""
from __future__ import annotations

import re

from alaya.providers.base import Call, Provider, Response, ToolSpec

_PERCEPT_LINE = re.compile(r"^\s*·\s*\[([^\]]+)\]\s*(.+)$", re.MULTILINE)


class EchoProvider(Provider):
    name = "echo"

    def __init__(self, script: list[list[Call]] | None = None):
        """``script`` drives deterministic behaviour in tests: one list of calls
        per round. Without it, the provider improvises from the rendered world."""
        self._script = script
        self._round = 0

    def converse(self, system: str, messages: list[dict], tools: list[ToolSpec]) -> Response:
        if self._script is not None:
            calls = self._script[self._round] if self._round < len(self._script) else []
            self._round += 1
            return Response(text=None, calls=list(calls))
        return self._improvise(messages)

    def _improvise(self, messages: list[dict]) -> Response:
        if self._round > 0:
            self._round = 0
            return Response(text="(echo) done")
        self._round += 1

        user = next((m["content"] for m in messages if m["role"] == "user"), "")
        text = user if isinstance(user, str) else str(user)
        percepts = _PERCEPT_LINE.findall(text)
        if not percepts:
            return Response(text="(echo) nothing arose; staying quiet.")

        sense, signal = percepts[0]
        sense = sense.split("·")[0].strip()
        return Response(
            text=None,
            calls=[
                Call(name="speak", args={"text": f"my {sense} has something: {signal}"}, id="e1"),
                Call(name="remember", args={"content": f"{sense}: {signal}"}, id="e2"),
            ],
        )
