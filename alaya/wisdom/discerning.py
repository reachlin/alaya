"""妙觀察智 — the sixth consciousness turned.

Wondrous observing wisdom. The sixth is the layer that discriminates, so its
transformation is not the end of discrimination but discrimination that no
longer overreaches: 觀察諸法自相共相無礙自在 — seeing the particular and general
characteristics of things without obstruction, and 說法斷疑, resolving doubt
rather than manufacturing certainty.

因中轉 — this begins at 見道, while practice is still under way, because
分別 is the thing wisdom can address most directly. So it runs online, every
cycle, and it is cheap.

WHAT IT ACTUALLY MEASURES
The rope-snake gate already tags every claim. This wisdom reads those tags back
and asks how much of what the agent has been saying was borne by anything. Then
it writes a directive to the layer that will read it a moment later — the
agent's own record correcting the agent's own discrimination, with nobody
in the loop.
"""
from __future__ import annotations

from collections import Counter

from alaya.seeds import Kind, Nature, Pramana
from alaya.wisdom.base import Basis, Progress, Stage

DISCRIMINATING = (Kind.CLAIM, Kind.DERIVED)


class Discerning:
    wisdom = "妙觀察智"
    roman = "discerning"
    layer = "第六意識"
    stage = Stage.CAUSE

    def __init__(self, window: int = 100):
        self.window = window

    def measure(self, basis: Basis) -> Progress:
        recent = [s for s in basis.store.all()[-self.window:] if s.kind in DISCRIMINATING]
        if not recent:
            return Progress(self.wisdom, self.roman, self.layer, self.stage, score=1.0,
                            metrics={"claims": 0},
                            notes=("nothing discriminated yet — nothing to correct",))

        fabricated = [s for s in recent if s.nature is Nature.PARIKALPITA]
        unfounded = [s for s in recent if s.pramana is Pramana.APRAMANA]
        fabrication_rate = len(fabricated) / len(recent)
        unfounded_rate = len(unfounded) / len(recent)

        # What does it keep adding? The terms that show up across many
        # fabricated claims are the agent's habitual superimpositions — the
        # snake it reaches for, rather than any one mistake.
        from alaya.trisvabhava import terms_of

        habits = Counter(t for s in fabricated for t in terms_of(s.content))
        recurring = tuple(t for t, n in habits.most_common(5) if n > 1)

        notes = []
        if fabrication_rate > 0.5:
            notes.append(f"{fabrication_rate:.0%} of your claims exceed what arose")
        if recurring:
            notes.append(f"you keep adding: {', '.join(recurring)}")

        return Progress(
            self.wisdom, self.roman, self.layer, self.stage,
            score=1.0 - fabrication_rate,
            metrics={"claims": len(recent), "fabrication": fabrication_rate,
                     "unfounded": unfounded_rate, "recurring": recurring},
            notes=tuple(notes),
        )

    def turn(self, basis: Basis) -> Progress:
        progress = self.measure(basis)
        if basis.directive is None:
            return progress
        basis.directive.write(self._directive(progress.metrics))
        return Progress(**{**progress.__dict__, "changed": True})

    @staticmethod
    def _directive(metrics: dict) -> str:
        """Write to the layer that will read this a second from now.

        Concrete and second-person, because that is what the sixth consciousness
        can act on. "Be more careful" is not a directive; "call examine() before
        remember()" is.
        """
        if not metrics.get("claims"):
            return ("Attend to what is arising. Say what you have, and mark what you "
                    "are adding to it.")

        lines = []
        fabrication = metrics.get("fabrication", 0.0)
        unfounded = metrics.get("unfounded", 0.0)
        recurring = metrics.get("recurring", ())

        if fabrication > 0.5:
            lines.append(
                f"{fabrication:.0%} of your recent claims said more than anything that "
                "arose could bear. Call examine() on a claim before you remember it, and "
                "when the examination names an addition, say the smaller true thing instead."
            )
        elif fabrication > 0.2:
            lines.append(
                f"About {fabrication:.0%} of your claims add something to what arose. "
                "That is ordinary, but name the addition when you make it."
            )
        else:
            lines.append(
                "Your recent claims have largely been borne by what arose. Keep saying "
                "the smaller true thing; it is working."
            )

        if recurring:
            lines.append(
                "You keep reaching for the same additions: "
                + ", ".join(recurring)
                + ". Notice when you are about to supply one of these from habit rather "
                "than from anything present."
            )
        if unfounded > 0.4:
            lines.append(
                f"{unfounded:.0%} of your claims had nothing arise behind them at all. "
                "Use attend() to bring conditions to mind before concluding, rather than "
                "concluding into an empty moment."
            )
        return "\n\n".join(lines)
