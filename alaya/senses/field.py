"""五識身 — the five faculties taken together, as they actually operate.

The doctrine insists the eight are 一心識流的八重功能 — eight functions of one
stream, not eight minds. The same holds within the five: they do not take turns
and they do not negotiate. They arise together in a moment, each with whatever
it has, and what arises is simply *the moment*.

So ``gather()`` returns a flat list of everything that arose. A faculty with no
device contributes nothing and is not an error. A faculty that throws is
skipped and the rest of the moment still happens — a broken camera does not
deafen the agent, which sounds obvious until you write the naive version that
lets one exception abort the tick.

ORDER: injected first. What is already present arises before what has to be
fetched, which also means a human at the console is never queued behind a
one-second microphone read.
"""
from __future__ import annotations

from typing import Mapping

from alaya.senses.base import DormantFaculty, Faculty
from alaya.senses.ear import Ear
from alaya.senses.eye import Eye
from alaya.senses.percept import Percept, Sense, Source


class SenseField:
    def __init__(self, faculties: Mapping[Sense, Faculty] | None = None):
        """Build the field.

        Pass nothing for the default arrangement: eye and ear live, the other
        three dormant. Pass a partial mapping to name only what you have — the
        rest are filled in dormant, so ``SenseField({Sense.BODY: MyBleSensor()})``
        is a complete field with one real faculty.
        """
        if faculties is None:
            faculties = {Sense.EYE: Eye(), Sense.EAR: Ear()}
        self.faculties: dict[Sense, Faculty] = {
            sense: faculties.get(sense) or DormantFaculty(sense) for sense in Sense
        }

    # ── arising ──────────────────────────────────────────────────────

    def gather(self) -> list[Percept]:
        """Everything that arose in this moment, injected feeds first."""
        percepts: list[Percept] = []
        for faculty in self.faculties.values():
            percepts.extend(faculty.drain())
        for faculty in self.faculties.values():
            try:
                percept = faculty.gather()
            except Exception:
                # 無心位 for this one faculty. The stream is not interrupted.
                continue
            if percept is not None:
                percepts.append(percept)
        return percepts

    def inject(
        self,
        sense: Sense,
        signal: str,
        source: Source = Source.INJECTED,
        extra: tuple[str, ...] = (),
    ) -> Percept:
        """Place a percept into one faculty — from the console, or from a bridge."""
        return self.faculties[sense].inject(signal, source=source, extra=extra)

    # ── 根身 — the body, as reported to the world ────────────────────

    def available(self) -> dict[Sense, bool]:
        """Which faculties have a feed. Never probes the hardware to find out."""
        return {sense: faculty.available for sense, faculty in self.faculties.items()}

    def close(self) -> None:
        for faculty in self.faculties.values():
            try:
                faculty.close()
            except Exception:
                pass
