"""现行熏种子 — perfuming, and the tick that holds it.

The three moments of the causal engine — 种子生现行, 现行熏种子, 种子生种子 —
are not three steps. They are one transaction (三法展转，因果同时). ``Tick`` is
that transaction: what activates and what is perfumed share a single moment,
and either both land or neither does.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Iterable

from alaya.seeds.seed import (
    Kind,
    LineageError,
    Nature,
    ProvenanceError,
    Seed,
    SimultaneityError,
    TickClosedError,
    Valence,
    ValenceError,
)

if TYPE_CHECKING:  # pragma: no cover
    from alaya.seeds.store import SeedStore


class Tick:
    """One moment of the stream. 因果同时 — cause and fruit commit together."""

    def __init__(self, store: "SeedStore", number: int):
        self._store = store
        self.number = number
        self._activated: dict[str, Seed] = {}
        self._staged: list[Seed] = []
        self._staged_by_id: dict[str, Seed] = {}
        self._last_moment: datetime | None = None
        self._open = True

    # ── 种子生现行 ───────────────────────────────────────────────────

    def activate(self, conditions: Iterable[str], limit: int | None = None) -> list[Seed]:
        """Fire every seed whose conditions are met (待众缘), strongest first."""
        self._require_open()
        fired = self._store.activate(conditions, now_tick=self.number, limit=limit)
        for seed in fired:
            self._activated[seed.id] = seed
        return fired

    # ── 现行熏种子 ───────────────────────────────────────────────────

    def perfume(
        self,
        content: str,
        kind: Kind,
        valence: Valence,
        nature: Nature,
        conditions: Iterable[str] = (),
        parents: Iterable[str] = (),
        weight: float = 1.0,
        lineage: str | None = None,
    ) -> Seed:
        """Lay down a new seed in this moment. Its causes must be present here."""
        self._require_open()
        parents = tuple(str(p) for p in parents)

        self._check_provenance(parents)
        if Kind(kind) is Kind.DERIVED:
            self._check_valence(parents, Valence(valence))
        lineage = self._resolve_lineage(lineage, parents)

        seed = Seed.arise(
            tick=self.number,
            at=self._moment(),
            kind=kind,
            content=content,
            valence=valence,
            nature=nature,
            conditions=conditions,
            parents=parents,
            weight=weight,
            lineage=lineage,
        )
        self._staged.append(seed)
        self._staged_by_id[seed.id] = seed
        return seed

    # ── invariants ───────────────────────────────────────────────────

    def _check_provenance(self, parents: tuple[str, ...]) -> None:
        """引自果 and 果俱有 — every cause must exist, and must be present now."""
        for pid in parents:
            known = self._store.has(pid) or pid in self._staged_by_id
            if not known:
                raise ProvenanceError(
                    f"引自果 — parent {pid[:12]}… is not in the store; "
                    "an effect must name a cause that exists"
                )
            present = pid in self._activated or pid in self._staged_by_id
            if not present:
                raise SimultaneityError(
                    f"果俱有 — parent {pid[:12]}… was not activated in tick {self.number}; "
                    "a cause must be present with its fruit, not merely on record"
                )

    def _check_valence(self, parents: tuple[str, ...], valence: Valence) -> None:
        """性决定 — 种子生种子 bears fruit of its own kind, never its opposite."""
        for parent in (self._seed(pid) for pid in parents):
            if parent.valence is not valence:
                raise ValenceError(
                    f"性决定 — a derived seed cannot turn {parent.valence.value} "
                    f"into {valence.value}"
                )

    def _resolve_lineage(self, lineage: str | None, parents: tuple[str, ...]) -> str | None:
        """自类相续 — continuing a line requires standing in it."""
        if lineage is None:
            return None
        if not (self._store.has_lineage(lineage) or any(
            self._seed(pid).lineage == lineage for pid in parents
        )):
            raise LineageError(f"自类相续 — no such lineage {lineage[:12]}…")
        if not any(self._seed(pid).lineage == lineage for pid in parents):
            raise LineageError(
                f"自类相续 — lineage {lineage[:12]}… continued from a seed outside it; "
                "self-continuity is of one kind with itself"
            )
        return lineage

    # ── helpers ──────────────────────────────────────────────────────

    def _seed(self, seed_id: str) -> Seed:
        if seed_id in self._staged_by_id:
            return self._staged_by_id[seed_id]
        return self._store.get(seed_id)

    def _moment(self) -> str:
        """刹那 — no two seeds occupy the same instant."""
        now = datetime.now(timezone.utc)
        if self._last_moment is not None and now <= self._last_moment:
            now = self._last_moment + timedelta(microseconds=1)
        self._last_moment = now
        return now.isoformat()

    def _require_open(self) -> None:
        if not self._open:
            raise TickClosedError(f"tick {self.number} has already passed")

    # ── the transaction ──────────────────────────────────────────────

    def __enter__(self) -> "Tick":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self._open = False
        if exc_type is None:
            self._store._commit(self._staged)
        self._staged.clear()
        return False
