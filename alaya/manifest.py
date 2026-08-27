"""變現 — how a world gets made out of a store.

THE CLAIM THIS FILE IMPLEMENTS
------------------------------
唯識 is often misheard as "the world is your hallucination". It says something
narrower and much harder to argue with: 一切法不離識 — whatever you can point
to, name, or check has *already* arrived in a form consciousness constructed.
There is no separate, independently-standing object available for comparison,
because reaching for one is itself another act of consciousness.

The doctrine's term for the constructing is 變現, "transforming-into-
appearance". The 阿賴耶識 變現 two things at once:

    器世間 (bhājana-loka)   the receptacle world — the environment
    根身  (sādhiṣṭhāna)     the embodied faculties — the agent's own body

Both are projections *from* the seed store. Neither is raw input.

WHY AN AGENT SHOULD BE BUILT THIS WAY ANYWAY
--------------------------------------------
Set the metaphysics aside; the engineering claim stands on its own. An agent's
context window is not the world. It is a small assembly the retrieval layer
构造ed out of storage, and the model can only deliberate over that assembly.
Retrieval *is* world-construction, and pretending otherwise — treating the
context as "what is true" rather than "what arose" — is the source of a whole
family of bugs where an agent confidently acts on the absence of something it
simply never retrieved.

So :func:`manifest` does not hand the model the sensor feed. It takes the
percepts, reads off the conditions they carry, asks the store what those
conditions cause to arise (種子生現行), and returns the assembly. What arose is
recorded, so any act citing it is traceable.

A COMMON MISREADING, WORTH NAMING
---------------------------------
器世間 is 共變 — collectively conditioned, produced by the shared karma (共業)
of many beings. That is the doctrine's own answer to "then why do two people
see the same mountain?", and it is why 唯識 is *not* solipsism; reading it as
private hallucination contradicts its own account. Nothing here implements 共業
— a shared world across agents is a real extension and an unbuilt one. It is
named so the gap is visible rather than papered over.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from alaya.seeds import Seed, Tick
from alaya.senses import Percept, Sense, Source


@dataclass(frozen=True)
class Body:
    """根身 — the agent as it appears to itself: what it can sense and do."""

    tick: int
    senses: Mapping[Sense, bool]
    tools: tuple[str, ...]

    def render(self) -> str:
        if self.senses:
            feeds = " · ".join(
                f"{sense.value} {'open' if live else '—'}" for sense, live in self.senses.items()
            )
        else:
            feeds = "(no faculties)"
        tools = ", ".join(self.tools) if self.tools else "(none)"
        return f"senses: {feeds}\ntools: {tools}"


@dataclass(frozen=True)
class World:
    """器世間 — one moment, assembled. This is what the sixth consciousness sees."""

    tick: int
    percepts: tuple[Percept, ...]
    active: tuple[Seed, ...]
    conditions: frozenset[str]
    body: Body

    @property
    def images(self) -> tuple[str, ...]:
        """Frames travel to the model as images, not as sentences about images."""
        return tuple(p.media for p in self.percepts if p.media)

    def render(self) -> str:
        lines = [f"MOMENT {self.tick}", "", "WHAT AROSE (現量 — signals, not names):"]
        if self.percepts:
            for p in self.percepts:
                mark = f"{p.sense.value} · injected" if p.source is Source.INJECTED else p.sense.value
                lines.append(f"  · [{mark}] {p.signal}")
        else:
            lines.append("  · nothing — no faculty reported this moment")

        lines += ["", "WHAT THE STORE PUT HERE (種子生現行 — seeds your conditions fired):"]
        if self.active:
            for s in self.active:
                lines.append(f"  · {s.content}   ({s.kind.value}/{s.pramana.value}, {s.id[:8]})")
        else:
            lines.append("  · nothing arose — no stored seed had its conditions met")

        lines += ["", "根身 (your body):", self.body.render()]
        return "\n".join(lines)


def manifest(
    tick: Tick,
    percepts: Iterable[Percept],
    senses: Mapping[Sense, bool],
    tools: Iterable[str],
    extra_conditions: Iterable[str] = (),
) -> World:
    """Build the moment. 變現 — the world is produced, not received.

    ``extra_conditions`` is 作意 (manaskāra, attention): volition adding a
    condition so that something otherwise dormant can arise. 待眾緣 says a seed
    fires only when its conditions are complete; attention is how an agent
    completes them on purpose rather than waiting for the world to do it.
    """
    percepts = tuple(percepts)
    conditions = frozenset(
        c for p in percepts for c in p.conditions
    ) | frozenset(extra_conditions)

    # 種子生現行 — and because this happens inside the tick, every seed that
    # arises here is a legitimate parent for anything perfumed later in the
    # same moment. That is 果俱有 doing its work.
    active = tuple(tick.activate(conditions))

    return World(
        tick=tick.number,
        percepts=percepts,
        active=active,
        conditions=conditions,
        body=Body(tick=tick.number, senses=dict(senses), tools=tuple(tools)),
    )
