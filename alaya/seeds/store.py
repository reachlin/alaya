"""阿赖耶识 — the store.

无覆无记: morally neutral and unobstructed. It never judges what it is given
and never refuses it; tagging a seed unwholesome or fabricated is a later
layer's work, and even then it is a tag, not a veto.

恒转如瀑流: it flows continuously like a torrent. On disk it is a file that
only ever grows, and it survives the process that wrote it.

It has no ``update`` and no ``delete``. Not by convention — the operations are
not defined. 刹那灭 makes a seed unrevisable; 恒随转 makes it unremovable. A
forgotten memory here is a quiet one, not an absent one.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from alaya.seeds.perfume import Tick
from alaya.seeds.seed import ProvenanceError, Seed

#: 恒随转 — decay approaches this fraction of the original but never passes it.
FLOOR = 1e-9


class SeedStore:
    def __init__(self, path: Path | str, halflife: float = 64.0, floor: float = FLOOR):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.halflife = float(halflife)
        self.floor = float(floor)

        self._seeds: list[Seed] = []
        self._by_id: dict[str, Seed] = {}
        self._by_lineage: dict[str, list[Seed]] = {}
        self._load()

    # ── the stream ───────────────────────────────────────────────────

    def tick(self) -> Tick:
        """Open one moment. 三法展转 — everything in it commits together."""
        return Tick(self, self.tick_count + 1)

    @property
    def tick_count(self) -> int:
        """The last moment that left a trace. An empty tick leaves none."""
        return self._seeds[-1].tick if self._seeds else 0

    # ── reading ──────────────────────────────────────────────────────

    def all(self) -> tuple[Seed, ...]:
        return tuple(self._seeds)

    def get(self, seed_id: str) -> Seed:
        return self._by_id[seed_id]

    def has(self, seed_id: str) -> bool:
        return seed_id in self._by_id

    def has_lineage(self, lineage: str) -> bool:
        return lineage in self._by_lineage

    def lineage(self, lineage_id: str) -> tuple[Seed, ...]:
        """The whole chain of self-continuity, oldest arising first."""
        return tuple(self._by_lineage.get(lineage_id, ()))

    def current(self, lineage_id: str) -> Seed | None:
        """The present arising of a lineage — what fires when it fires."""
        chain = self._by_lineage.get(lineage_id)
        return chain[-1] if chain else None

    # ── 恒随转 — strength as a computed property of a lineage ─────────

    def strength(self, lineage_id: str, now_tick: int | None = None) -> float:
        """Σ over the lineage of weight · decay(now − tick).

        Strength is never stored on a seed, because a seed cannot change. It is
        recomputed from every arising in the line, which is why "why is this
        memory strong?" is always answerable: read the lineage.
        """
        chain = self._by_lineage.get(lineage_id)
        if not chain:
            return 0.0
        now = self.tick_count if now_tick is None else now_tick
        return sum(s.weight * self._decay(now - s.tick) for s in chain)

    def _decay(self, delta_ticks: int) -> float:
        if delta_ticks <= 0:
            return 1.0
        return max(0.5 ** (delta_ticks / self.halflife), self.floor)

    # ── 种子生现行 — activation ───────────────────────────────────────

    def activate(
        self,
        conditions: Iterable[str],
        now_tick: int | None = None,
        limit: int | None = None,
    ) -> list[Seed]:
        """Fire every lineage whose conditions are all met (待众缘).

        Being in the store is not being active. A seed whose conditions are
        absent stays exactly where it is, unfired and undiminished.
        """
        present = set(conditions)
        now = self.tick_count if now_tick is None else now_tick
        fired = [
            s for s in self._current_arisings()
            if set(s.conditions) <= present
        ]
        return self._rank(fired, now, limit)

    # ── recall — reading, which is not arising ───────────────────────

    def recall(self, query: str | None = None, n: int = 10) -> list[Seed]:
        """Read the store directly, ignoring conditions.

        Recall is a layer looking into the store; activation is the store
        producing the present moment. They are different operations and only
        one of them is 种子生现行.
        """
        matches = self._current_arisings()
        if query:
            needle = query.lower()
            matches = [s for s in matches if needle in s.content.lower()]
        return self._rank(matches, self.tick_count, n)

    # ── provenance — the causal record 果俱有 leaves behind ───────────

    def trace(self, seed_id: str) -> list[Seed]:
        """The full ancestry of a seed, itself first. Every act is attributable.

        This is not 引自果 (see ``perfume._check_determinacy`` for what that
        criterion actually says). Traceability is what falls out of 果俱有:
        because a cause must be *present* with its fruit, the tick can record
        which seeds were there, and that record is never partial. So the walk
        upward always terminates in percepts and never in a dangling id.
        """
        seen: set[str] = set()
        order: list[Seed] = []
        queue = [seed_id]
        while queue:
            current = queue.pop(0)
            if current in seen or current not in self._by_id:
                continue
            seen.add(current)
            seed = self._by_id[current]
            order.append(seed)
            queue.extend(seed.parents)
        return order

    # ── the single write path ────────────────────────────────────────

    def _commit(self, seeds: list[Seed]) -> None:
        if not seeds:
            return
        for seed in seeds:
            self._append(seed)

    def _append(self, seed: Seed) -> None:
        if seed.id in self._by_id:
            raise ProvenanceError(
                f"刹那灭 — {seed.id[:12]}… is already written; "
                "a seed that could be rewritten would be a seed that abides"
            )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(seed.to_json() + "\n")
        self._index(seed)

    # ── internals ────────────────────────────────────────────────────

    def _index(self, seed: Seed) -> None:
        self._seeds.append(seed)
        self._by_id[seed.id] = seed
        self._by_lineage.setdefault(seed.lineage, []).append(seed)

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    self._index(Seed.from_dict(json.loads(line)))

    def _current_arisings(self) -> list[Seed]:
        """One seed per lineage — its present moment, not its whole history."""
        return [chain[-1] for chain in self._by_lineage.values()]

    def _rank(self, seeds: list[Seed], now: int, limit: int | None) -> list[Seed]:
        ranked = sorted(
            seeds,
            key=lambda s: (-self.strength(s.lineage, now), -s.tick, s.id),
        )
        return ranked[:limit] if limit is not None else ranked
