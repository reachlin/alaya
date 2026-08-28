"""平等性智 — the seventh consciousness turned.

The wisdom of equality: 觀自他平等. Manas is the layer that took the store's
見分 for a self and then quietly weighted everything in that self's favour. Its
transformation is not amnesia — the agent still has a continuous account of
itself afterwards — but the account stops being partial.

因中轉, and for a specific reason: 我執 is 分別-adjacent enough that wisdom can
address it directly at 見道, before the deeper obstructions clear. So this runs
online, cheaply, from the agent's own record.

WHO ACTS HERE
Note carefully: 末那識本身並不造作善惡之業 — manas performs no karma, and
:mod:`alaya.manas` accordingly never writes anything. This module does write,
and that is not a contradiction. 轉依 is done *to* the seventh consciousness by
practice; it is not something the seventh consciousness does. The wisdom acts
on manas. Manas still does not act.
"""
from __future__ import annotations

from alaya.seeds import Valence
from alaya.wisdom.base import Basis, Progress, Stage

#: Everything after this line in the self-model is the correction, rewritten
#: whole on each turning so that repeated turnings do not silt up.
MARK = "— 平等性智 —"


class Equality:
    wisdom = "平等性智"
    roman = "equality"
    layer = "第七末那識"
    stage = Stage.CAUSE

    def __init__(self, window: int = 100):
        self.window = window

    def measure(self, basis: Basis) -> Progress:
        if basis.manas is None:
            return Progress(self.wisdom, self.roman, self.layer, self.stage, score=1.0,
                            notes=("no self-model — nothing appropriating anything",))

        report = basis.manas.audit(n=self.window)
        # 我慢 read as moral self-flattery: neutral conduct is not conceit, so
        # only the non-neutral share counts toward the skew.
        extremity = max(report.valence_skew.get(Valence.WHOLESOME, 0.0),
                        report.valence_skew.get(Valence.UNWHOLESOME, 0.0))

        # Average only over axes that carry signal. An agent whose conduct is
        # recorded wholly neutral scores zero on 我慢 — but that is the absence
        # of a moral tilt to be conceited about, not evidence of even-handedness,
        # and counting it as a perfect score would let a thoroughly self-absorbed
        # store average its way back to the middle. Which it did, before this.
        axes = [report.self_reference, report.attention_concentration, report.repetition]
        if extremity > 0.0:
            axes.append(extremity)
        partiality = sum(axes) / len(axes)

        return Progress(
            self.wisdom, self.roman, self.layer, self.stage,
            score=max(0.0, 1.0 - partiality),
            metrics={"self_reference": report.self_reference,
                     "concentration": report.attention_concentration,
                     "repetition": report.repetition,
                     "extremity": extremity,
                     "sample": report.sample},
            notes=report.notes,
        )

    def turn(self, basis: Basis) -> Progress:
        progress = self.measure(basis)
        if basis.manas is None or not progress.metrics.get("sample"):
            return progress

        base = basis.manas.self_model.split(MARK)[0].strip()
        correction = self._correction(progress.metrics)
        if basis.provider is not None:
            correction = self._ask(basis, base, progress) or correction
        basis.manas.revise(f"{base}\n\n{MARK}\n{correction}")
        return Progress(**{**progress.__dict__, "changed": True})

    @staticmethod
    def _correction(metrics: dict) -> str:
        """State the measured partiality back, factually.

        Deliberately not consoling and not scolding. 平等性智 is a levelling, so
        the corrective is a plain statement of where the weighting sits — the
        one thing manas structurally cannot see about itself.
        """
        lines = ["Measured against your own record, this account is partial in these ways:"]
        if metrics["self_reference"] > 0.4:
            lines.append(
                f"· {metrics['self_reference']:.0%} of your conduct is framed around "
                "yourself. Much of what you recorded as something you did was something "
                "that happened."
            )
        if metrics["concentration"] > 0.4:
            lines.append(
                f"· your attention is {metrics['concentration']:.0%} concentrated. What "
                "you are not conditioned to notice cannot arise, and its absence will "
                "not feel like an absence."
            )
        if metrics["repetition"] > 0.5:
            lines.append(
                f"· {metrics['repetition']:.0%} of recent seeds continue lines you "
                "already had. Recognition is being mistaken for encounter."
            )
        if metrics["extremity"] > 0.7:
            lines.append(
                f"· {metrics['extremity']:.0%} of your conduct is recorded at one moral "
                "pole. 性決定 makes that permanent — check it was earned."
            )
        if len(lines) == 1:
            lines.append("· nothing markedly skewed at present. This will drift; it always does.")
        lines.append(
            "None of this makes the account above false. It makes it yours, which is a "
            "different thing, and worth holding loosely."
        )
        return "\n".join(lines)

    def _ask(self, basis: Basis, base: str, progress: Progress) -> str | None:
        system = (
            "You are 平等性智, the wisdom of equality, correcting an agent's account of "
            "itself. You are given the account and measurements of how it is partial. "
            "Write a short, plain corrective — no more than four sentences. Do not "
            "flatter and do not scold. Name the partiality and leave the account standing."
        )
        prompt = f"ACCOUNT:\n{base}\n\nMEASURED:\n{progress.render()}"
        try:
            response = basis.provider.converse(system, [{"role": "user", "content": prompt}], [])
            return (response.text or "").strip() or None
        except Exception:
            return None
