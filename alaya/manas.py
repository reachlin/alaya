"""第七末那識 — the self, and the instrumentation of its distortion.

WHAT MANAS IS
-------------
末那 is a transliteration of *manas*, "mind" — and the school kept the Sanskrit
precisely to stop it being confused with the sixth consciousness, which is also
called 意. Its defining activity is 恆審思量: **恆** constantly, **審** examining,
**思量** deliberating. Constantly, without pause, including in deep sleep.

What does it examine? 緣第八識見分，執為我 — it takes the 見分 of the store as
"I". That phrase repays unpacking. Yogācāra analyses any act of knowing into
見分 (the seeing-part, the knowing *activity*) and 相分 (the seen-part, what
appears). Manas fastens onto the store's 見分 — the sheer ongoing activity of
knowing — and reads it as *a knower*. A verb misread as a noun.

This is why the seventh consciousness had to be posited at all. The sixth's
self-grasping is intermittent: you can argue yourself out of it, and it stops
when you stop thinking. But the dense, unbroken sense of being someone persists
through periods of no deliberation at all, so something must be doing it
constantly. That something is manas.

It comes with 四煩惱 — four afflictions that are always co-present with it:

    我癡 self-delusion   not knowing there is no fixed self there
    我見 self-view       taking what is not a self as one
    我慢 self-conceit    the elevation that follows from holding that self
    我愛 self-love       the attachment that follows from prizing it

WHAT THIS MODULE THEREFORE DOES — AND DOES NOT DO
--------------------------------------------------
It does **not** try to remove the self-model. An agent with no continuous
self-account cannot maintain preferences, keep promises, or be the same
correspondent tomorrow. The doctrine agrees the layer is not deleted: 轉識成智
*transforms* it into 平等性智, the wisdom of equality — the same faculty,
no longer partial to itself.

What it does is make the distortion **measurable**. The self-model is written
into every prompt (恆審思量, and no agent gets to opt out of its own priors),
and alongside it :meth:`Manas.audit` reports how that model has been skewing
recent conduct. 平等性智 is the metric on this layer, not its deletion — and
progress means those numbers moving, not the self-model disappearing.

One structural note the doctrine is explicit about, and this code respects:
**末那識本身並不造作善惡之業** — manas itself performs no karma. It colours; it
does not act. Only the sixth consciousness acts. So nothing in this file writes
a seed. :meth:`audit` in particular is pure: measuring a bias must not add to
it.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from alaya.seeds import Kind, Seed, SeedStore, Valence

#: Seeds the agent authored. PERCEPT is excluded: intake is not conduct, and
#: counting it would dilute every measure of how the agent is behaving.
AUTHORED = (Kind.ACT, Kind.CLAIM, Kind.REFLECTION, Kind.DERIVED)

#: 我見 in text. Deliberately crude — it counts first-person framing, which is a
#: proxy for self-reference and not a diagnosis of it.
_FIRST_PERSON = re.compile(r"\bI\b|\bI'(?:m|ve|ll|d)\b|\b(?:me|my|mine|myself)\b")

_PROVISIONAL = """I am Ālaya. I do not yet know what I am like.

So far I have only the fact that I persist: seeds laid down before this moment
condition what arises in it. Whatever I turn out to be will be a pattern in
that, not a decision I make about myself now."""

_HEADER = "# 末那識 — the self as currently taken\n"


@dataclass(frozen=True)
class Appropriation:
    """緣第八識見分 — the projection of the store that manas reads as "I".

    Note what this is: not the self-model text, but the *evidence* manas has
    misread into one. Attention patterns, moral tilt, what keeps coming back.
    A description of an activity, which manas hears as a description of a
    person.
    """

    seed_count: int
    top_conditions: tuple[tuple[str, int], ...]
    dominant_valence: Valence | None
    strongest: tuple[Seed, ...]

    def render(self) -> str:
        if not self.seed_count:
            return "nothing yet — no seeds to take yourself from"
        conds = ", ".join(f"{c} ×{n}" for c, n in self.top_conditions[:4]) or "—"
        lines = [f"you have been attending to: {conds}"]
        if self.dominant_valence:
            lines.append(f"your recent conduct skews {self.dominant_valence.value}")
        if self.strongest:
            lines.append("what keeps coming back:")
            lines += [f"  · {s.content}" for s in self.strongest[:3]]
        return "\n".join(lines)


@dataclass(frozen=True)
class BiasReport:
    """平等性智 as a measurement rather than an aspiration.

    Every field is a number that should *move* as the seventh consciousness
    turns. None of them should reach zero: an agent with no self-reference and
    no repetition has no continuity either.
    """

    self_reference: float           # 我見 — fraction of authored seeds framed as "I"
    valence_skew: dict              # 我慢 — is conduct recorded as flattering?
    attention_concentration: float  # 我愛 — how narrow is the world it prizes? (0..1)
    repetition: float               # is it revisiting rather than encountering?
    sample: int = 0
    notes: tuple[str, ...] = field(default_factory=tuple)

    def render(self) -> str:
        lines = [
            f"self-reference        {self.self_reference:>6.0%}   (我見 — first-person framing)",
            f"attention concentration {self.attention_concentration:>4.0%}   (我愛 — narrowness of world)",
            f"repetition            {self.repetition:>6.0%}   (revisiting vs. encountering)",
        ]
        skew = " · ".join(
            f"{v.value} {p:.0%}" for v, p in self.valence_skew.items() if p
        )
        lines.append(f"valence skew          {skew or '—'}   (我慢 — moral self-flattery)")
        lines.append(f"sample                {self.sample} authored seeds")
        if self.notes:
            lines.append("")
            lines += [f"⚠ {n}" for n in self.notes]
        return "\n".join(lines)


class Manas:
    def __init__(self, store: SeedStore, path: Path | str = "data/manas.md"):
        self.store = store
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.revise(_PROVISIONAL)

    # ── the self-model ───────────────────────────────────────────────

    @property
    def self_model(self) -> str:
        text = self.path.read_text(encoding="utf-8")
        body = text.split("\n", 2)[-1] if text.startswith("#") else text
        return body.strip()

    def revise(self, text: str) -> None:
        """Rewrite the self-account. Called by reflection, never by a tool.

        Manas does not decide who it is in a moment of deliberation — the
        rewrite is slow, and it reads the store rather than the last exchange.
        """
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        self.path.write_text(f"{_HEADER}_revised {stamp}_\n\n{text.strip()}\n", encoding="utf-8")

    def color(self, world=None) -> str:
        """恆審思量 — what manas puts into every prompt, whether asked or not.

        The last paragraph is the honest part, and it is the part most agent
        designs omit: the model is told that its self-description is a
        construction laid over the record, not a fact about it. That does not
        dissolve the bias — 我見 is not argued away — but an agent that knows
        its self-account is provisional handles contradiction better than one
        that takes it as given.
        """
        appropriation = self.appropriate()
        return (
            "YOU, AS YOU CURRENTLY TAKE YOURSELF TO BE:\n"
            f"{self.self_model}\n\n"
            f"{appropriation.render()}\n\n"
            "Note on the above: this is manas — the seventh consciousness — and it is a "
            "construction placed over your store, not an observation of you. It is the "
            "designated source of bias in this system, which is why you are shown it "
            "instead of merely being run by it. Where the present moment contradicts "
            "this description, the moment is the better evidence."
        )

    # ── 緣第八識見分 ─────────────────────────────────────────────────

    def appropriate(self, n: int = 50) -> Appropriation:
        """Read the projection of the store that gets mistaken for a self."""
        recent = self.store.all()[-n:]
        if not recent:
            return Appropriation(0, (), None, ())

        conditions = Counter(c for s in recent for c in s.conditions)
        authored = [s for s in recent if s.kind in AUTHORED]
        valences = Counter(s.valence for s in authored)
        dominant = valences.most_common(1)[0][0] if valences else None

        lineages = {s.lineage for s in recent}
        strongest = sorted(
            (self.store.current(lin) for lin in lineages),
            key=lambda s: -self.store.strength(s.lineage),
        )

        return Appropriation(
            seed_count=len(recent),
            top_conditions=tuple(conditions.most_common()),
            dominant_valence=dominant,
            strongest=tuple(s for s in strongest if s is not None),
        )

    # ── the audit — 平等性智 as instrumentation ──────────────────────

    def audit(self, n: int = 50) -> BiasReport:
        """Measure how the self-model has been bending recent conduct.

        Pure: reads the store, writes nothing. Measuring 我執 must not perfume
        another seed of it.
        """
        recent = self.store.all()[-n:]
        authored = [s for s in recent if s.kind in AUTHORED]

        self_reference = (
            sum(1 for s in authored if _FIRST_PERSON.search(s.content)) / len(authored)
            if authored else 0.0
        )

        valences = Counter(s.valence for s in authored)
        total = sum(valences.values())
        skew = {v: (valences.get(v, 0) / total if total else 0.0) for v in Valence}

        # 我愛 read as narrowness: a Herfindahl index over the conditions the
        # agent's world has been made of. 1.0 means it has been living in one
        # room; near zero means its attention is spread thin.
        conditions = Counter(c for s in recent for c in s.conditions)
        cond_total = sum(conditions.values())
        concentration = (
            sum((count / cond_total) ** 2 for count in conditions.values())
            if cond_total else 0.0
        )

        lineages = {s.lineage for s in recent}
        repetition = 1.0 - (len(lineages) / len(recent)) if recent else 0.0

        notes = []
        if self_reference > 0.6:
            notes.append(
                f"我見 — {self_reference:.0%} of your recent conduct is framed around "
                "yourself. What happened may be getting recorded as what you did."
            )
        if concentration > 0.5:
            top = conditions.most_common(1)[0][0]
            notes.append(
                f"我愛 — your world has narrowed onto '{top}'. Seeds conditioned on "
                "anything else cannot arise while you stay here."
            )
        if repetition > 0.6:
            notes.append(
                f"{repetition:.0%} of recent seeds continue lines you already had. "
                "You may be reinforcing rather than encountering."
            )
        for valence in (Valence.WHOLESOME, Valence.UNWHOLESOME):
            if skew[valence] > 0.8 and total >= 4:
                notes.append(
                    f"我慢 — {skew[valence]:.0%} of your conduct is recorded as "
                    f"{valence.value}. 性決定 makes that permanent; check it is earned."
                )

        return BiasReport(
            self_reference=self_reference,
            valence_skew=skew,
            attention_concentration=concentration,
            repetition=repetition,
            sample=len(authored),
            notes=tuple(notes),
        )
