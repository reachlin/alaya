"""种子 — the seed, as an immutable, content-addressed unit.

A seed is 刹那灭: it arises, and in arising it is already complete and already
past. Nothing about it can be revised. What looks like a memory changing over
time is a lineage — one seed perishing and re-arising as another of its own
kind (自类相续). See ``store.SeedStore.strength``.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Iterable


class SeedError(ValueError):
    """A seed that could not validly arise."""


class ProvenanceError(SeedError):
    """引自果 — an effect whose cause cannot be resolved."""


class SimultaneityError(SeedError):
    """果俱有 — a cause offered in a moment it was not present in."""


class ValenceError(SeedError):
    """性决定 — fruit of a different nature than the seed that bore it."""


class KindError(SeedError):
    """引自果 — 色心不相互生: fruit of a category other than the seed's own."""


class LineageError(SeedError):
    """自类相续 — a continuity claimed between things not of one kind."""


class TickClosedError(SeedError):
    """A moment that has already passed."""


class Kind(str, Enum):
    PERCEPT = "percept"        # 现量 — bare intake from the sense layer
    ACT = "act"                # 造业 — something the agent did to the world
    CLAIM = "claim"            # a proposition the agent holds
    REFLECTION = "reflection"  # the seventh consciousness looking at the store
    DERIVED = "derived"        # 种子生种子 — produced from other seeds alone


class Valence(str, Enum):
    """性决定 — fixed at the moment of perfuming, never revised."""

    WHOLESOME = "wholesome"
    UNWHOLESOME = "unwholesome"
    NEUTRAL = "neutral"


class Nature(str, Enum):
    """三性 — an ontology. What kind of thing this is."""

    PARATANTRA = "paratantra"        # 依他起 — dependently arisen; 似有非实
    PARIKALPITA = "parikalpita"      # 遍计所执 — fabricated; 情有理无
    PARINISPANNA = "parinispanna"    # 圆成实 — what remains when fabrication is stripped


class Pramana(str, Enum):
    """三量 — an epistemology. How this came to be known.

    Orthogonal to :class:`Nature`. A dependently-arisen rope is 依他起 whether
    or not the cognition of it is sound; whether *this* cognition is sound is
    what 三量 answers. 非量 is the doctrine's own name for the rope taken for a
    snake, which is why the erroneous class lives on this axis.
    """

    PRATYAKSA = "pratyaksa"    # 现量 — direct: present, manifest, undiscriminated
    ANUMANA = "anumana"        # 比量 — inferred: reached through conditions
    APRAMANA = "apramana"      # 非量 — erroneous: discrimination the object does not bear


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class Seed:
    """A single arising. Frozen, content-addressed, and final."""

    tick: int
    at: str
    kind: Kind
    content: str
    valence: Valence
    nature: Nature
    pramana: Pramana
    conditions: tuple[str, ...]
    parents: tuple[str, ...]
    weight: float
    lineage: str
    id: str = field(compare=True)

    # ── arising ──────────────────────────────────────────────────────

    @classmethod
    def arise(
        cls,
        *,
        tick: int,
        at: str,
        kind: Kind,
        content: str,
        valence: Valence,
        nature: Nature,
        pramana: Pramana | None = None,
        conditions: Iterable[str] = (),
        parents: Iterable[str] = (),
        weight: float = 1.0,
        lineage: str | None = None,
    ) -> "Seed":
        kind, valence, nature = Kind(kind), Valence(valence), Nature(nature)
        # 前五识唯现量 — the senses present and do not discriminate, so they can
        # neither infer nor err. Everything else defaults to inference, being
        # reached through conditions rather than borne directly.
        if pramana is None:
            pramana = Pramana.PRATYAKSA if kind is Kind.PERCEPT else Pramana.ANUMANA
        pramana = Pramana(pramana)
        conditions = tuple(sorted({str(c) for c in conditions}))
        parents = tuple(str(p) for p in parents)

        if not str(content).strip():
            raise SeedError("a seed with no content cannot arise")
        if weight <= 0:
            raise SeedError(f"weight must be positive, got {weight!r}")
        if kind is Kind.DERIVED and not parents:
            raise SeedError("a derived seed with no parents is an effect without a cause")
        if kind is Kind.PERCEPT and pramana is not Pramana.PRATYAKSA:
            raise SeedError(
                f"前五识唯现量 — a percept cannot be known by {pramana.value}; "
                "naming what a signal is *of* is already the sixth consciousness"
            )

        payload = {
            "tick": int(tick),
            "at": str(at),
            "kind": kind.value,
            "content": content,
            "valence": valence.value,
            "nature": nature.value,
            "pramana": pramana.value,
            "conditions": list(conditions),
            "parents": list(parents),
            "weight": float(weight),
            # a root's lineage is its own id, which is not yet known — hash it as empty
            "lineage": lineage or "",
        }
        seed_id = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()

        return cls(
            tick=int(tick),
            at=str(at),
            kind=kind,
            content=content,
            valence=valence,
            nature=nature,
            pramana=pramana,
            conditions=conditions,
            parents=parents,
            weight=float(weight),
            lineage=lineage or seed_id,
            id=seed_id,
        )

    # ── reading ──────────────────────────────────────────────────────

    @property
    def is_root(self) -> bool:
        """True when this seed begins its own line of continuity."""
        return self.lineage == self.id

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        d["valence"] = self.valence.value
        d["nature"] = self.nature.value
        d["pramana"] = self.pramana.value
        d["conditions"] = list(self.conditions)
        d["parents"] = list(self.parents)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Seed":
        return cls(
            tick=int(d["tick"]),
            at=d["at"],
            kind=Kind(d["kind"]),
            content=d["content"],
            valence=Valence(d["valence"]),
            nature=Nature(d["nature"]),
            pramana=Pramana(d.get("pramana", Pramana.ANUMANA.value)),
            conditions=tuple(d["conditions"]),
            parents=tuple(d["parents"]),
            weight=float(d["weight"]),
            lineage=d["lineage"],
            id=d["id"],
        )

    def to_json(self) -> str:
        return _canonical(self.to_dict())
