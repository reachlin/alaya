"""大圓鏡智 — the eighth consciousness turned.

The great perfect mirror wisdom. A mirror holds everything put in front of it,
adds nothing, prefers nothing, and is not changed by what it shows. That is the
ālaya with 執藏 gone — still the store of all seeds, no longer something manas
can grasp as a self.

果上圓, and the most emphatically so of the four: the store turns last, at
Buddhahood, because everything else rests on it.

WHAT THE TRANSFORMATION LOOKS LIKE IN CODE
A mirror is undistorted, and the distortion an append-only store accumulates is
**redundancy**. Fifty near-identical arisings of one event do not make it
fifty times more true; they make retrieval fifty times noisier and crowd out
everything else that might have arisen. A store like that reflects its own
history of attention rather than what was there.

So the turning is 種子生種子 — see :mod:`alaya.seeds.consolidate`. And note what
it cannot be: it cannot delete the fifty (恆隨轉) or rewrite them (剎那滅). It
adds one abstraction that arises more readily than any of them. The store gets
clearer without anything being lost, which is a strictly better property than
compaction and is forced on us by the invariants rather than chosen.
"""
from __future__ import annotations

from alaya.seeds.consolidate import cluster, consolidate, pending
from alaya.wisdom.base import Basis, Progress, Stage


class Mirror:
    wisdom = "大圓鏡智"
    roman = "mirror"
    layer = "第八阿賴耶識"
    stage = Stage.FRUIT

    def __init__(self, threshold: float = 0.6, limit: int | None = None):
        self.threshold = threshold
        self.limit = limit

    def measure(self, basis: Basis) -> Progress:
        # Measured over what is still *outstanding*: a cluster already abstracted
        # has been answered, and going on counting it would mean the score could
        # never respond to the very turning that addresses it.
        arisings = pending(basis.store)
        if not arisings:
            return Progress(self.wisdom, self.roman, self.layer, self.stage, score=1.0,
                            metrics={"arisings": 0}, notes=("the mirror is empty",))

        groups = cluster(arisings, threshold=self.threshold)
        crowded = sum(len(g.seeds) for g in groups)
        redundancy = crowded / len(arisings)

        notes = []
        if groups:
            biggest = max(groups, key=lambda g: len(g.seeds))
            notes.append(
                f"{len(groups)} thing(s) said {crowded} times — the largest "
                f"{len(biggest.seeds)}×: {biggest.shared and ', '.join(biggest.shared[:4])}"
            )
        return Progress(
            self.wisdom, self.roman, self.layer, self.stage,
            score=1.0 - redundancy,
            metrics={"arisings": len(arisings), "clusters": len(groups),
                     "redundancy": redundancy},
            notes=tuple(notes),
        )

    def turn(self, basis: Basis) -> Progress:
        progress = self.measure(basis)
        derived = consolidate(basis.store, threshold=self.threshold, limit=self.limit)
        if not derived:
            return progress
        return Progress(**{
            **progress.__dict__,
            "changed": True,
            "notes": progress.notes + (f"{len(derived)} abstraction(s) laid down; "
                                       "nothing removed",),
        })
