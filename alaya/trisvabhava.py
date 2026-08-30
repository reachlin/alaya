"""三性 — the rope-snake gate.

THE ILLUSTRATION, AND WHY IT IS EXACTLY RIGHT FOR THIS
------------------------------------------------------
《攝大乘論》: in dim light you see a coiled rope and recoil from a snake. Out of
that one situation the school reads three natures — and insists they are **not
three things**.

    遍計所執性  parikalpita-svabhāva — "the snake"
                情有理無: real to the frightened mind, with no own-being at all.
                Pure 名言 (verbal designation) laid over what is there. 全無自體.

    依他起性    paratantra-svabhāva — "the rope"
                眾緣所生, arisen from conditions. 似有非實 — present in the way
                conditioned things are present, which is *not* the way you
                thought the snake was present. It is 三性共同的所依, the common
                ground the other two are read off.

    圓成實性    pariniṣpanna-svabhāva — "the hemp"
                於依他起上遠離遍計所顯: what shows on the dependent once the
                fabrication is taken off it. Not a fourth thing hidden behind
                the rope — the same rope, no longer misread.

去掉蛇的是智慧，見到麻的是證悟 — 而繩始終是那條繩. Removing the snake is
wisdom; seeing the hemp is realisation; and the rope was the same rope the
whole time. **Nothing about the object changes at any point.** Only cognition
does. That is why this can be a gate on claims rather than a filter on data.

WHAT THE GATE DOES
------------------
An agent's claim is the snake. The percepts and seeds that actually arose are
the rope. :func:`examine` separates them, names the superimposition, and states
what may be said once it is removed.

EXPECT MOST CLAIMS TO COME BACK OVERLAID
-----------------------------------------
This is the part that surprises people reading the output. 遍計所執 is the
*ordinary* condition of unawakened cognition — the doctrine's claim is not that
superimposition is an occasional lapse but that it is what ordinary knowing
consists of. A gate that reported clean most of the time would be the broken
one. The useful signal is not "is there a snake" (there is, nearly always) but
"how much of this act rests on the snake".

A NOTE ON WHAT THIS CODE DOES NOT CLAIM
----------------------------------------
:meth:`Examination.restate` produces what the doctrine calls the residue, and
in the strict technical sense — 於依他起上遠離遍計所顯 — that is what 圓成實性
names. It would be a category error to read that as this program attaining
真如. 圓成實 in the full sense is 真如, suchness, the object of 根本智. Here it
means only: the dependent, restated without the addition. The narrow sense is
genuinely useful and the wide one is not being claimed.

三無性. Each nature has a corresponding non-nature — 相無性 (the fabricated has
no own-characteristic), 生無性 (the dependent has no own-arising), 勝義無性 (the
perfected is itself empty of own-nature). That triad is how Yogācāra absorbs
Prajñāpāramitā's 一切法空 without collapsing into nihilism: things lack own-being
in three different ways, not in one flat way. Nothing here implements it; it is
noted because it is the answer to "isn't 依他起 just realism with extra steps".
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Protocol, Sequence

from alaya.seeds import Nature, Pramana, Seed

#: Function words carry no evidential weight in either direction, so counting
#: them would let "the" and "is" inflate the support of a wholly invented claim.
STOPWORDS = frozenset("""
a an the this that these those there here and or but not no nor so then than
is are was were be been being am do does did doing have has had having
i you he she it we they me him her them my your his its our their
of in on at to for with from by as into onto about over under out up down off
if when while because since although though very just also too only even still
what which who whom whose how why where can could will would shall should may
might must ought seem seems seemed something someone anything anyone nothing
""".split())

_WORD = re.compile(r"[0-9a-zÀ-ɏ]+")


class Verdict(str, Enum):
    DEPENDENT = "dependent"    # 依他起 — the claim says only what arose
    OVERLAID = "overlaid"      # 遍計所執 over a real basis — the ordinary case
    UNFOUNDED = "unfounded"    # nothing that arose bears this at all


@dataclass(frozen=True)
class Examination:
    """One rope-snake examination. Pure data; nothing here touches the store."""

    claim: str
    terms: tuple[str, ...]        # the claim's content words
    supported: tuple[str, ...]    # those that what-arose actually bears
    fabricated: tuple[str, ...]   # 遍計所執 — those it does not
    dependent: tuple[str, ...]    # 依他起 — the ground contents themselves
    support: float                # fraction of the claim that arose
    verdict: Verdict
    note: str = ""

    @property
    def nature(self) -> Nature:
        """三性 for a seed carrying this claim.

        A claim that exceeds its basis is 遍計所執 *as held*, even though its
        basis is 依他起 — which is why OVERLAID and UNFOUNDED share a nature and
        are told apart on the other axis.
        """
        return Nature.PARATANTRA if self.verdict is Verdict.DEPENDENT else Nature.PARIKALPITA

    @property
    def measure(self) -> Pramana:
        """三量 as this examination alone would judge it.

        Read the caveat before using this. It reflects only what was passed in:
        an examiner that cannot see how a claim follows from its grounds will
        call a sound inference unfounded. :class:`~alaya.mano.Mano` therefore
        takes the measure from *provenance* — did anything arise to reason from
        — and lets the gate govern nature only. A lexical test must not be able
        to demote a genuine 比量 to 非量.
        """
        return Pramana.APRAMANA if self.verdict is Verdict.UNFOUNDED else Pramana.ANUMANA

    #: Beyond this many grounds the residue stops being a restatement and starts
    #: being a dump. 圓成實 is what remains *sayable*, so it has to stay sayable.
    SHOWN = 4

    def restate(self) -> str:
        """圓成實 in the narrow sense — the dependent, with the addition removed."""
        if not self.dependent:
            return "nothing arose; there is nothing here to say"
        shown = list(self.dependent[: self.SHOWN])
        rest = len(self.dependent) - len(shown)
        return " / ".join(shown) + (f" (and {rest} more)" if rest else "")

    def render(self) -> str:
        lines = [f"claim: {self.claim}", f"verdict: {self.verdict.value} ({self.support:.0%} of it arose)"]
        if self.fabricated:
            lines.append("遍計所執 (added by you, borne by nothing): " + ", ".join(self.fabricated))
        if self.dependent:
            shown = list(self.dependent[: self.SHOWN])
            rest = len(self.dependent) - len(shown)
            lines.append("依他起 (what actually arose): " + " / ".join(shown)
                         + (f" (and {rest} more)" if rest else ""))
        lines.append("without the addition, you have: " + self.restate())
        if self.note:
            lines.append(f"note: {self.note}")
        return "\n".join(lines)


# ── examiners ────────────────────────────────────────────────────────


class Examiner(Protocol):
    def examine(self, claim: str, grounds: Sequence[Seed]) -> Examination: ...


def terms_of(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 2}


class TermExaminer:
    """The default examiner: literal, deterministic, and deliberately blunt.

    It asks one question — does this word appear in what arose? — so it cannot
    see that "dark" follows from "luminance 0.02", and will report the claim
    unfounded. That failure direction is chosen: an examiner that guesses
    generously about what its grounds imply is an examiner that launders
    fabrication, which is the exact thing this gate exists to prevent. When
    semantic judgement is genuinely needed, use :class:`ModelExaminer`.
    """

    def examine(self, claim: str, grounds: Sequence[Seed]) -> Examination:
        grounds = list(grounds)
        claim_terms = terms_of(claim)

        # A percept's 待眾緣 tags are part of what arose, not metadata about it:
        # "sense:nose" firing *is* the nose having presented something.
        ground_text = " ".join(
            f"{s.content} {' '.join(s.conditions)}" for s in grounds
        )
        ground_terms = terms_of(ground_text)

        supported = claim_terms & ground_terms
        fabricated = claim_terms - supported
        support = len(supported) / len(claim_terms) if claim_terms else 0.0

        if not grounds or not claim_terms or not supported:
            verdict = Verdict.UNFOUNDED
        elif fabricated:
            verdict = Verdict.OVERLAID
        else:
            verdict = Verdict.DEPENDENT

        return Examination(
            claim=claim.strip(),
            terms=tuple(sorted(claim_terms)),
            supported=tuple(sorted(supported)),
            fabricated=tuple(sorted(fabricated)),
            dependent=tuple(s.content for s in grounds),
            support=support,
            verdict=verdict,
        )


_MODEL_SYSTEM = """You are performing 绳蛇检验, the rope-snake examination from Yogācāra.

You are given a CLAIM and the GROUNDS — everything that actually arose in this
moment. Your only job is to name what the claim adds that the grounds do not
bear: the 遍計所执 (fabricated superimposition), the snake laid over the rope.

Judge implication, not vocabulary. If the grounds say "luminance 0.02" and the
claim says "dark", that is borne — darkness is what low luminance is. If the
grounds say "pizza" and the claim says "my neighbour left it", the neighbour is
fabricated: nothing that arose bears them.

Reply with JSON only: {"fabricated": ["term", ...], "note": "one short line"}
An empty list means the claim says only what arose."""


class ModelExaminer:
    """A semantic examiner. Falls back to the literal one whenever it cannot answer.

    The fallback is not politeness. If the examiner is unavailable and we
    silently passed everything, the gate would fail *open* — every claim
    reported clean precisely when nothing was checking. Failing back to the
    blunt examiner fails closed.
    """

    def __init__(self, provider, fallback: Examiner | None = None):
        self.provider = provider
        self.fallback = fallback or TermExaminer()

    def examine(self, claim: str, grounds: Sequence[Seed]) -> Examination:
        base = self.fallback.examine(claim, grounds)
        if not grounds or not getattr(self.provider, "deliberative", True):
            return base

        prompt = (
            f"GROUNDS:\n" + "\n".join(f"- {s.content}" for s in grounds)
            + f"\n\nCLAIM:\n{claim}"
        )
        try:
            response = self.provider.converse(
                _MODEL_SYSTEM, [{"role": "user", "content": prompt}], []
            )
            data = json.loads(_json_of(response.text or ""))
            fabricated = tuple(sorted(str(t).lower() for t in data.get("fabricated", [])))
            note = str(data.get("note", ""))
        except Exception:
            return base

        supported = tuple(t for t in base.terms if t not in fabricated)
        support = len(supported) / len(base.terms) if base.terms else 0.0
        if not supported:
            verdict = Verdict.UNFOUNDED
        elif fabricated:
            verdict = Verdict.OVERLAID
        else:
            verdict = Verdict.DEPENDENT

        return Examination(
            claim=base.claim, terms=base.terms, supported=supported,
            fabricated=fabricated, dependent=base.dependent,
            support=support, verdict=verdict, note=note,
        )


def _json_of(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if 0 <= start < end else text


# ── the gate as mano uses it ─────────────────────────────────────────


@dataclass
class RopeSnake:
    """The gate in the action path.

    ``strict`` decides what an unfounded outward act does. Default is to
    **mark, not block** — which is 無覆無記 carried up from the store: the
    system's job is to make the superimposition visible, not to censor a mind
    for having one. Set ``strict=True`` where an agent's speech has
    consequences, and an act resting on nothing is refused with the residue
    handed back so the model can say the true smaller thing instead.
    """

    examiner: Examiner = field(default_factory=TermExaminer)
    strict: bool = False

    def examine(self, claim: str, grounds: Iterable[Seed]) -> Examination:
        return self.examiner.examine(claim, list(grounds))

    def permits(self, examination: Examination) -> bool:
        return not (self.strict and examination.verdict is Verdict.UNFOUNDED)


def examine(claim: str, grounds: Iterable[Seed], examiner: Examiner | None = None) -> Examination:
    """Run one rope-snake examination. Pure — writes nothing anywhere."""
    return (examiner or TermExaminer()).examine(claim, list(grounds))
