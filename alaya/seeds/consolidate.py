"""種子生種子 — the third causal moment, and the only one that stays inside.

種子生現行 and 現行熏種子 both cross between latent and manifest. This one does
not: it is 自類相續 operating on a whole store, a line of seeds succeeding
itself into something more general than any of its members.

WHY IT CANNOT BE A GARBAGE COLLECTOR
------------------------------------
The obvious thing to do with fifty near-identical memories is to merge them
into one and drop the rest. Both halves are forbidden here — 剎那滅 makes seeds
unrewritable, 恆隨轉 makes them unremovable — and the prohibition is right
rather than inconvenient. A store that quietly deletes has no answer to "why do
you believe that?", and a store that quietly edits has a worse one.

So consolidation is **additive**. The cluster stays exactly where it is. A new
DERIVED seed is perfumed alongside it, carrying the *intersection* of the
members' conditions, which means it fires in every situation any member would
have fired in. Retrieval then surfaces one abstraction instead of fifty
near-duplicates — not because the fifty went away, but because the abstraction
arises more readily than any of them.

果俱有 THEN FORCES THE INTERESTING PART
---------------------------------------
To name the fifty as parents they must be *present*, so the consolidator has to
make them arise first — it opens a tick and activates them before deriving
anything. **You cannot abstract from memories you have not actually recalled.**
That is not a constraint anyone designed into this function; it falls out of
the second criterion, and it is exactly the right behaviour.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from alaya.seeds.seed import Kind, Nature, Pramana, Seed, Valence
from alaya.seeds.store import SeedStore

#: Jaccard overlap over content words above which two seeds count as one thing
#: said twice. Deliberately lexical, like the default rope-snake examiner:
#: a consolidator that guessed at meaning would fuse things that merely sound
#: alike, and unlike a bad retrieval that fusion is permanent.
THRESHOLD = 0.6


def _terms(text: str) -> set[str]:
    from alaya.trisvabhava import terms_of

    return terms_of(text)


@dataclass(frozen=True)
class Cluster:
    kind: Kind
    valence: Valence
    seeds: tuple[Seed, ...]
    shared: tuple[str, ...]

    @property
    def conditions(self) -> tuple[str, ...]:
        """The intersection — the fewest requirements any member needed."""
        common: set[str] | None = None
        for seed in self.seeds:
            common = set(seed.conditions) if common is None else common & set(seed.conditions)
        return tuple(sorted(common or ()))

    def summary(self) -> str:
        longest = max(self.seeds, key=lambda s: len(s.content))
        return f"{longest.content} — and {len(self.seeds) - 1} more like it ({len(self.seeds)} arisings)"


def cluster(
    seeds: Iterable[Seed], threshold: float = THRESHOLD, min_size: int = 2
) -> list[Cluster]:
    """Group seeds that are one thing said several times. Pure — writes nothing.

    Grouping is confined within 引自果 and 性決定: never across kinds, because a
    derived seed drawn from a mixture of categories is refused outright, and
    never across valences, because 善種 and 惡種 are different lines whatever
    they have in common lexically.
    """
    candidates = [
        (s, _terms(s.content)) for s in seeds
        # An abstraction of abstractions compounds whatever the first pass got
        # wrong, and there is no way to walk it back.
        if s.kind is not Kind.DERIVED and _terms(s.content)
    ]
    used: set[str] = set()
    clusters: list[Cluster] = []

    for seed, terms in candidates:
        if seed.id in used:
            continue
        group = [(seed, terms)]
        for other, other_terms in candidates:
            if other.id in used or other.id == seed.id:
                continue
            if other.kind is not seed.kind or other.valence is not seed.valence:
                continue
            overlap = len(terms & other_terms) / len(terms | other_terms)
            if overlap >= threshold:
                group.append((other, other_terms))
        if len(group) < min_size:
            continue
        for member, _ in group:
            used.add(member.id)
        shared: set[str] = set.intersection(*(t for _, t in group))
        clusters.append(Cluster(
            kind=seed.kind, valence=seed.valence,
            seeds=tuple(m for m, _ in group), shared=tuple(sorted(shared)),
        ))
    return clusters


def pending(store: SeedStore) -> list[Seed]:
    """Arisings that have not already borne this fruit.

    Because consolidation removes nothing, the originals are still present
    arisings afterwards. Anything already cited by a DERIVED seed has produced
    its abstraction and does not produce it again — otherwise a second pass
    would re-abstract the same cluster forever, and any measure of redundancy
    would go on reporting a crowd that has already been answered.
    """
    spent = {
        parent
        for seed in store.all() if seed.kind is Kind.DERIVED
        for parent in seed.parents
    }
    return [s for s in store.arisings() if s.id not in spent]


def consolidate(
    store: SeedStore,
    threshold: float = THRESHOLD,
    min_size: int = 2,
    limit: int | None = None,
) -> list[Seed]:
    """Run one pass of 種子生種子 over the store. Additive; nothing is removed.

    Idempotent — see :func:`pending` for why that takes explicit work here.
    """
    clusters = cluster(pending(store), threshold=threshold, min_size=min_size)
    if limit is not None:
        clusters = clusters[:limit]
    if not clusters:
        return []

    derived: list[Seed] = []
    with store.tick() as t:
        for group in clusters:
            # 果俱有 — make them arise before citing them. The union of their
            # conditions is guaranteed to fire every member, since 待眾緣 asks
            # only that a seed's own conditions be a subset of what is present.
            present = {c for s in group.seeds for c in s.conditions}
            arisen = {s.id for s in t.activate(present)}
            members = [s for s in group.seeds if s.id in arisen]
            if len(members) < min_size:
                continue
            derived.append(t.perfume(
                content=group.summary(),
                kind=Kind.DERIVED,
                valence=group.valence,          # 性決定 — the line keeps its nature
                nature=Nature.PARATANTRA,
                # An abstraction is reached *through* its members, never borne
                # directly. 前五識唯現量 does not apply here, but the same logic
                # does: nothing about a generalisation is directly perceived.
                pramana=Pramana.ANUMANA,
                conditions=group.conditions,
                parents=[s.id for s in members],
                weight=sum(s.weight for s in members) / len(members),
            ))
    return derived
