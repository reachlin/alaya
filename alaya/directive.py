"""The standing instruction the sixth consciousness reads each moment.

Distinct from :mod:`alaya.identity`, and the distinction matters. 本願 does not
move; this does. The directive is what 妙觀察智 writes when it turns — the
agent's own practice correcting how it discriminates, phrased as guidance to
the layer that will read it a second later.

That is 因中轉 in one file: revisable while running, derived from the agent's
own record rather than from anyone's instruction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

_PROVISIONAL = (
    "Attend to what is actually arising. The senses give you signals, not names — "
    "say what you have, and mark what you are adding to it."
)

_HEADER = "# 妙觀察智 — the standing directive\n"


class Directive:
    def __init__(self, path: Path | str = "data/directive.md"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.write(_PROVISIONAL)

    def read(self) -> str:
        text = self.path.read_text(encoding="utf-8")
        return (text.split("\n", 2)[-1] if text.startswith("#") else text).strip()

    def write(self, text: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        self.path.write_text(f"{_HEADER}_turned {stamp}_\n\n{text.strip()}\n", encoding="utf-8")
