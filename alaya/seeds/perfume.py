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
    KindError,
    LineageError,
    Nature,
    Pramana,
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
        pramana: Pramana | None = None,
        conditions: Iterable[str] = (),
        parents: Iterable[str] = (),
        weight: float = 1.0,
        lineage: str | None = None,
    ) -> Seed:
        """Lay down a new seed in this moment. Its causes must be present here.

        現行熏種子 — "manifest activity perfumes seeds". The metaphor is incense:
        activity does not *put* anything into the store, it leaves a scent on it,
        a disposition to arise that way again. Every gate below refuses a seed
        that could not have been perfumed by what was actually happening.
        """
        self._require_open()
        parents = tuple(str(p) for p in parents)

        self._check_provenance(parents)
        self._check_determinacy(parents, Kind(kind), Valence(valence))
        lineage = self._resolve_lineage(lineage, parents, Kind(kind))

        seed = Seed.arise(
            tick=self.number,
            at=self._moment(),
            kind=kind,
            content=content,
            valence=valence,
            nature=nature,
            pramana=pramana,
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
        """果俱有 — the cause must be *present*, not merely on file.

        果俱有 (kārya-sahabhū, "existing together with its fruit") is the second
        of the 種子六義. It denies that causation is a relay across time: the
        seed, its manifestation, and the fruit are simultaneous, arising and
        ceasing together in one 刹那. There is no moment in which the cause
        waits around for the effect.

        That yields two distinguishable failures, and the distinction matters:

        * the cause **does not exist** — an effect naming nothing. A provenance
          failure, and the reason ``trace()`` can never dead-end.
        * the cause **exists but is not here** — a seed sitting in the store
          that nothing caused to arise this moment. Citing it would make it a
          cause acting at a distance in time, which is exactly what 果俱有 rules
          out.
        """
        for pid in parents:
            known = self._store.has(pid) or pid in self._staged_by_id
            if not known:
                raise ProvenanceError(
                    f"parent {pid[:12]}… is not in the store; "
                    "an effect must name a cause that exists"
                )
            present = pid in self._activated or pid in self._staged_by_id
            if not present:
                raise SimultaneityError(
                    f"果俱有 — parent {pid[:12]}… was not activated in tick {self.number}; "
                    "a cause must be present with its fruit, not merely on record"
                )

    def _check_determinacy(self, parents: tuple[str, ...], kind: Kind, valence: Valence) -> None:
        """性決定 and 引自果 — the two determinacy criteria, which are siblings.

        性決定 (fourth criterion) fixes the *moral* category: 善種生善現行,
        惡種生惡現行. A wholesome seed yields wholesome manifestation. It cannot
        curdle into its opposite on the way out, which is what stops a store of
        past conduct from being quietly relabelled by later interpretation.

        引自果 (sixth criterion) fixes the *ontological* category, and the
        classical formula for it is 色心不相互生 — form and mind do not produce
        one another. Each seed 引 (draws forth) 自果 (its own fruit): a seed of
        matter yields matter, a seed of mind yields mind.

        Note what 引自果 is *not*. It is not "provenance is traceable" — that is
        a consequence of 果俱有 recording the link, and an earlier draft of this
        file had it wrong. 引自果 is a determinacy rule, and its code form is
        category preservation, exactly parallel to 性決定 above.
        """
        if kind is not Kind.DERIVED:
            return
        for parent in (self._seed(pid) for pid in parents):
            if parent.valence is not valence:
                raise ValenceError(
                    f"性決定 — a derived seed cannot turn {parent.valence.value} "
                    f"into {valence.value}"
                )
        kinds = {self._seed(pid).kind for pid in parents}
        if len(kinds) > 1:
            named = ", ".join(sorted(k.value for k in kinds))
            raise KindError(
                f"引自果 — 色心不相互生: a derived seed cannot be drawn from a "
                f"mixture of categories ({named})"
            )

    def _resolve_lineage(
        self, lineage: str | None, parents: tuple[str, ...], kind: Kind
    ) -> str | None:
        """自類相續 — continuing a line requires standing in it, as its own kind.

        自類相續 ("continuity of its own category") is how the doctrine keeps
        剎那滅 from destroying 恆隨轉. A seed is momentary, so nothing persists;
        yet karma must carry. The resolution is that the seed perishes and
        re-arises *as one of its own kind*, an unbroken succession of similar
        moments rather than one thing enduring — 恆隨轉 is glossed 如瀑流,
        "like a waterfall", which looks continuous while no water stays.

        Two conditions follow, and both are enforced here:

        * you may only continue a line you actually stand in (a parent in it),
        * and you must continue it as its own 類 — hence the ``kind`` check,
          which is 引自果 applied along the axis of succession.
        """
        if lineage is None:
            return None
        in_line = [self._seed(pid) for pid in parents if self._seed(pid).lineage == lineage]
        if not (self._store.has_lineage(lineage) or in_line):
            raise LineageError(f"自類相續 — no such lineage {lineage[:12]}…")
        if not in_line:
            raise LineageError(
                f"自類相續 — lineage {lineage[:12]}… continued from a seed outside it; "
                "self-continuity is of one kind with itself"
            )
        established = self._store.lineage(lineage)
        root_kind = established[0].kind if established else in_line[0].kind
        if kind is not root_kind:
            raise KindError(
                f"引自果 — 色心不相互生: a {root_kind.value} lineage cannot continue "
                f"as {kind.value}"
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
