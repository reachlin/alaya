"""共業 — the shared world, and why it is not a shared store.

THE OBJECTION THIS ANSWERS
--------------------------
If everything is 唯識, why do you and I see the same river? 《唯識二十論》 treats
this as one of the four strongest objections to the whole position — 多人共見,
many people seeing one thing — and it does not answer by conceding an external
river. It answers with 共業: the 器世間 is 共變, collectively transformed,
manifested congruently by beings whose karma is shared.

That is the school's defence against being read as solipsism, and it is not a
patch. An implementation that skipped it would leave the architecture looking
like private hallucination, which is precisely the misreading the source text
opens by refuting. So this module exists to close that gap.

WHAT IT IS EMPHATICALLY NOT
---------------------------
There is no shared store here, and there must not be. **The ālaya is
individual.** Each being has one; a universal or cosmic mind is a different
doctrine belonging to a different school, and conflating them is one of the two
or three most common errors made with this material.

So two agents never share a store. What passes between them is 共相種子 —
common seeds — immutable records that each agent perfumes into its *own*
stream and manifests for itself. 各自變現: each transforms its own. The worlds
come to look alike because the seeds are alike, not because there is one world
object both are pointed at.

That distinction is the entire doctrine. It also happens to be the better
distributed design: no shared mutable state, only propagation of
content-addressed records into per-agent stores.

共 AND 不共 — WHAT TRAVELS
--------------------------
The classical division sorts what the store manifests into what is held in
common and what is not:

    共業  → 共相種子 → 器世間, the receptacle world, held in common
    不共業 → 不共相種子 → 根身, one's own embodied faculties, held alone

Percepts are 根身. What your ear did is not a thing anyone else can be handed —
only what you made of it can be. So percepts never travel, and neither do
reflections, which are self-model material. Claims, derivations and acts do.

Received seeds are 比量 without exception. You did not perceive it; at best you
infer it from the fact that someone said so. Dignāga folds testimony (聖教量)
into inference for exactly this reason, and nothing another agent tells you is
ever 現量 in your own stream.

ONE DELIBERATE DEPARTURE
------------------------
By default fabrication does not travel: a claim tagged 遍計所執 or 非量 stays
home. The doctrine would not agree. 共業 explains shared *delusion* every bit as
well as it explains shared rivers — a crowd coming to see the same thing that
is not there is a textbook case of it, and arguably the more interesting half.

The default here is nonetheless to withhold, because a system that gossips
unfounded claims between agents manufactures consensus out of nothing, and
consensus is precisely what an observer would then mistake for evidence. Pass
``only_borne=False`` for the faithful behaviour, which is worth watching once.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from alaya.seeds import Kind, Nature, Pramana, Seed, SeedStore, Valence

#: 不共 — manifested by karma that is one's own alone, and never offered.
PRIVATE_KINDS = (Kind.PERCEPT, Kind.REFLECTION)

#: 共 — of the receptacle world, and shareable.
COMMON_KINDS = (Kind.CLAIM, Kind.DERIVED, Kind.ACT)

#: Condition prefixes belonging to 根身 rather than 器世間. Which of *your*
#: faculties presented something is yours even when the claim is not.
PRIVATE_PREFIXES = ("sense:", "source:", "level:", "form:")


def _key(content: str, kind: Kind, valence: Valence, conditions: tuple[str, ...]) -> str:
    """A name for a common seed that every agent computes identically.

    Not a seed id: those carry tick, moment and lineage, which are properties of
    one stream and cannot mean anything in another. This is a name for the
    *content* held in common — 共相, the shared characteristic.
    """
    payload = json.dumps(
        [content, kind.value, valence.value, sorted(conditions)],
        ensure_ascii=False, separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Offering:
    """One 共相種子, in transit. Immutable, like everything else here."""

    key: str
    origin: str
    content: str
    kind: str
    valence: str
    conditions: tuple[str, ...]
    at: str

    def to_json(self) -> str:
        return json.dumps(
            {**asdict(self), "conditions": list(self.conditions)},
            ensure_ascii=False, separators=(",", ":"), sort_keys=True,
        )

    @classmethod
    def from_dict(cls, d: dict) -> "Offering":
        return cls(key=d["key"], origin=d["origin"], content=d["content"],
                   kind=d["kind"], valence=d["valence"],
                   conditions=tuple(d["conditions"]), at=d["at"])


class Commons:
    """器世間 as a channel of common seeds — never as a store two agents share."""

    def __init__(self, path: Path | str, only_borne: bool = True):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.only_borne = only_borne

    # ── reading the channel ──────────────────────────────────────────

    def offerings(self) -> list[Offering]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as fh:
            return [Offering.from_dict(json.loads(line)) for line in fh if line.strip()]

    # ── 熏 into the common — publishing ──────────────────────────────

    def offer(self, store: SeedStore, agent: str) -> list[Offering]:
        """Publish this agent's 共相種子. Additive and idempotent."""
        already = {o.key for o in self.offerings()}
        published: list[Offering] = []

        with self.path.open("a", encoding="utf-8") as fh:
            for seed in store.arisings():
                if seed.kind in PRIVATE_KINDS:
                    continue                       # 不共 — 根身 does not travel
                if any(c.startswith("from:") for c in seed.conditions):
                    continue                       # already someone else's; do not echo
                if self.only_borne and (
                    seed.nature is Nature.PARIKALPITA or seed.pramana is Pramana.APRAMANA
                ):
                    continue
                conditions = self._common_conditions(seed.conditions)
                key = _key(seed.content, seed.kind, seed.valence, conditions)
                if key in already:
                    continue
                offering = Offering(
                    key=key, origin=agent, content=seed.content,
                    kind=seed.kind.value, valence=seed.valence.value,
                    conditions=conditions, at=seed.at,
                )
                fh.write(offering.to_json() + "\n")
                already.add(key)
                published.append(offering)
        return published

    # ── 變現 from the common — receiving ─────────────────────────────

    def receive(self, store: SeedStore, agent: str) -> list[Seed]:
        """Perfume other agents' common seeds into *this* store.

        The receiving agent makes its own seed. It does not acquire anyone
        else's — 各自變現, each transforms its own, and two agents holding
        congruent worlds is the whole of what 共業 claims.

        Received seeds are roots: they have no local parent, because there is no
        local cause. That looks like a provenance gap and is instead an accurate
        one — ``from:<origin>`` records that this arrived by testimony, and a
        trace bottoming out there is telling the truth about what the agent has.

        Note what is *not* written into ``conditions``: a bookkeeping key. An
        earlier draft tagged received seeds ``common:<hash>`` to make
        idempotence trivial, which quietly broke the feature outright —
        conditions are 待眾緣, requirements for *arising*, and no moment will
        ever present a hash. Every received seed was therefore inert, sitting in
        the store unable to fire. Recognition is done by fingerprint instead,
        and conditions carry only things that can actually be present.
        """
        held = {self._fingerprint(seed) for seed in store.all()}
        incoming = [
            o for o in self.offerings()
            if o.origin != agent
            and (o.origin, o.content, o.valence, o.conditions) not in held
        ]
        if not incoming:
            return []

        received: list[Seed] = []
        with store.tick() as t:
            for offering in incoming:
                received.append(t.perfume(
                    content=offering.content,
                    # Whatever it was where it came from, here it is something
                    # this agent holds on report — a claim, not a doing.
                    kind=Kind.CLAIM,
                    valence=Valence(offering.valence),   # 性決定 survives transit
                    nature=Nature.PARATANTRA,
                    # 聖教量 folded into 比量: you did not perceive this, you
                    # infer it from the fact that someone said so.
                    pramana=Pramana.ANUMANA,
                    conditions=(*offering.conditions, f"from:{offering.origin}"),
                ))
        return received

    # ── internals ────────────────────────────────────────────────────

    @staticmethod
    def _common_conditions(conditions: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            c for c in conditions
            if not c.startswith(PRIVATE_PREFIXES) and not c.startswith("from:")
        )

    @staticmethod
    def _fingerprint(seed: Seed) -> tuple | None:
        """What a received seed looks like from the offering side.

        Reconstructed rather than stored, so nothing has to be kept outside the
        store and nothing unpresentable has to go into ``conditions``.
        """
        origin = next((c[len("from:"):] for c in seed.conditions
                       if c.startswith("from:")), None)
        if origin is None:
            return None
        conditions = tuple(c for c in seed.conditions if not c.startswith("from:"))
        return (origin, seed.content, seed.valence.value, conditions)
