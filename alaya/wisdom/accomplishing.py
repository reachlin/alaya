"""成所作智 — the five sense consciousnesses turned.

成辦所應作事 — accomplishing what is to be done. The five senses transformed
are the faculties working *well*: presenting what is actually there, at the
right sensitivity, in the service of what needs doing.

果上圓, and the reason is exactly the engineering reason. A faculty cannot be
recalibrated from inside its own operation — you cannot judge whether the ear's
threshold is right from one reading, only from the record of many, and only
while nothing is reading. So this needs the stream stopped.

WHAT IT MEASURES
Attribution. For each faculty: how much did it present, and how much of that
ended up behind an act? A faculty producing a great deal that grounds nothing is
not neutral — every silent percept is a seed perfumed, a lineage started, and
context spent. A faculty producing nothing at all may be the one that matters
and simply has no device attached.
"""
from __future__ import annotations

from collections import Counter

from alaya.seeds import Kind
from alaya.senses import Sense
from alaya.wisdom.base import Basis, Progress, Stage

#: Fraction of silent readings above which the ear is listening past the room,
#: and below which it is calling room tone a sound.
TOO_QUIET, TOO_LOUD = 0.9, 0.2


class Accomplishing:
    wisdom = "成所作智"
    roman = "accomplishing"
    layer = "前五識"
    stage = Stage.FRUIT

    def measure(self, basis: Basis) -> Progress:
        seeds = basis.store.all()
        percepts = [s for s in seeds if s.kind is Kind.PERCEPT]
        if not percepts:
            return Progress(self.wisdom, self.roman, self.layer, self.stage, score=1.0,
                            metrics={"yield": {}}, notes=("no faculty has presented anything",))

        # Everything any act was ever built on. 果俱有 guarantees this walk is
        # total: a cause had to be present to be cited, so nothing is missing.
        grounding: set[str] = set()
        for act in (s for s in seeds if s.kind is Kind.ACT):
            grounding.update(a.id for a in basis.store.trace(act.id))

        presented: Counter = Counter()
        grounded: Counter = Counter()
        silent: Counter = Counter()
        for seed in percepts:
            for condition in seed.conditions:
                if not condition.startswith("sense:"):
                    continue
                sense = condition.split(":", 1)[1]
                presented[sense] += 1
                if seed.id in grounding:
                    grounded[sense] += 1
                if "level:silent" in seed.conditions:
                    silent[sense] += 1

        yields = {s: grounded[s] / presented[s] for s in presented}
        notes = []
        for sense, ratio in sorted(yields.items()):
            if presented[sense] >= 3 and ratio == 0.0:
                notes.append(
                    f"{sense}: {presented[sense]} arisings, none behind any act — "
                    "presenting into nothing"
                )
        for sense, count in silent.items():
            share = count / presented[sense]
            if share > TOO_QUIET and presented[sense] >= 3:
                notes.append(f"{sense}: {share:.0%} silence — the threshold is above the room")

        overall = sum(grounded.values()) / sum(presented.values())
        return Progress(
            self.wisdom, self.roman, self.layer, self.stage,
            score=overall,
            metrics={"yield": yields, "presented": dict(presented),
                     "silent": dict(silent)},
            notes=tuple(notes),
        )

    def turn(self, basis: Basis) -> Progress:
        """Recalibrate what can be recalibrated. Report the rest.

        Only the ear's threshold is adjusted automatically — it is a number with
        an obvious target and a bounded blast radius. Everything else (a faculty
        with no device, a sense carrying all the traffic) is reported for a human,
        because 成所作智 accomplishing what is *to be done* does not license a
        program rewriting its own hardware assumptions.
        """
        progress = self.measure(basis)
        if basis.senses is None:
            return progress

        faculty = basis.senses.faculties.get(Sense.EAR)
        gate = getattr(faculty, "gate", None)
        presented = progress.metrics.get("presented", {}).get("ear", 0)
        if gate is None or presented < 3:
            return progress

        share = progress.metrics.get("silent", {}).get("ear", 0) / presented
        if share > TOO_QUIET:
            faculty.gate = max(gate * 0.5, 1e-4)     # hearing nothing — listen closer
        elif share < TOO_LOUD:
            faculty.gate = min(gate * 1.5, 0.5)      # hearing everything — room tone is not sound
        else:
            return progress

        return Progress(**{**progress.__dict__, "changed": True,
                           "notes": progress.notes + (f"ear threshold {gate:.4f} → "
                                                      f"{faculty.gate:.4f}",)})
