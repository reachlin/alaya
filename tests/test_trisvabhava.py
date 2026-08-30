"""三性 — the rope, the snake, and what is left when the snake is taken away.

《攝大乘論》 gives the illustration: in dim light you see a coiled rope and
recoil from a snake. Three natures, and the whole point is that they are **not
three things**:

    遍計所執性  the snake — 情有理無, real to the frightened mind, with no
                own-being whatever. Purely 名言 laid over what is there.
    依他起性    the rope  — 眾緣所生, dependently arisen. 似有非實: it is there
                in the way conditioned things are there, which is not the way
                you thought the snake was there. It is the common ground of all
                three natures.
    圓成實性    the hemp  — 於依他起上遠離遍計所顯. Not a fourth thing behind
                the rope: it is the rope, seen without the snake on it.

去掉蛇的是智慧，見到麻的是證悟 — 而繩始終是那條繩. Nothing about the rope
changes at any point. Only the cognition does.

WHAT THAT MEANS FOR AN AGENT
An agent's claims are the snake. The percepts and seeds that actually arose are
the rope. This module separates them, names the superimposition, and states
what may be said with the superimposition removed.

Note the expected result: **most ordinary claims come back OVERLAID.** That is
not the gate malfunctioning. 遍計所執 is the ordinary condition of unawakened
cognition, not an exceptional failure — a gate that reported clean most of the
time would be the one that was broken.
"""
import pytest

from alaya.seeds import Kind, Nature, Pramana, Valence
from alaya.trisvabhava import (
    Examination,
    ModelExaminer,
    TermExaminer,
    Verdict,
    examine,
)
from tests.conftest import percept as seed_of


def grounds(store, *contents, conditions=()):
    with store.tick() as t:
        return [seed_of(t, c, conditions=conditions) for c in contents]


# ── the three verdicts ───────────────────────────────────────────────

def test_a_claim_that_says_only_what_arose_is_dependent(store):
    g = grounds(store, "pizza, cooling on the counter")
    result = examine("pizza cooling", g)
    assert result.verdict is Verdict.DEPENDENT
    assert result.fabricated == ()


def test_a_claim_that_adds_something_is_overlaid(store):
    """The rope is really there. The snake is what you put on it."""
    g = grounds(store, "pizza, cooling")
    result = examine("pizza cooling, left by my neighbour", g)
    assert result.verdict is Verdict.OVERLAID
    assert "neighbour" in result.fabricated


def test_a_claim_with_nothing_behind_it_is_unfounded(store):
    result = examine("someone is at the door", [])
    assert result.verdict is Verdict.UNFOUNDED


def test_a_claim_sharing_nothing_with_what_arose_is_unfounded(store):
    """Grounds existing is not the same as grounds bearing *this*."""
    g = grounds(store, "pizza, cooling")
    result = examine("the tide is going out", g)
    assert result.verdict is Verdict.UNFOUNDED
    assert result.support == 0.0


# ── the partition ────────────────────────────────────────────────────

def test_dependent_and_fabricated_partition_the_claim(store):
    """Three readings of one thing — so nothing may fall between them."""
    g = grounds(store, "pizza, cooling")
    result = examine("cold pizza on the counter", g)
    assert set(result.supported) | set(result.fabricated) == set(result.terms)
    assert set(result.supported) & set(result.fabricated) == set()


def test_support_is_the_fraction_that_arose(store):
    g = grounds(store, "alpha bravo")
    result = examine("alpha bravo charlie delta", g)
    assert result.support == 0.5


def test_conditions_count_as_part_of_what_arose(store):
    """A percept's 待眾緣 tags are part of the moment, not metadata about it."""
    g = grounds(store, "pizza", conditions=("sense:nose",))
    assert examine("nose: pizza", g).verdict is Verdict.DEPENDENT


def test_stopwords_are_not_evidence_of_anything(store):
    g = grounds(store, "pizza")
    result = examine("the pizza is on the thing that is there", g)
    assert "the" not in result.terms
    assert "is" not in result.terms


def test_an_empty_claim_is_unfounded(store):
    assert examine("   ", grounds(store, "pizza")).verdict is Verdict.UNFOUNDED


# ── 圓成實 — the residue ─────────────────────────────────────────────

def test_restating_gives_back_the_dependent_alone(store):
    """圓成實 is not a fourth thing. It is the rope with the snake removed."""
    g = grounds(store, "pizza, cooling on the counter")
    result = examine("pizza left by my neighbour", g)
    restated = result.restate()
    assert "pizza, cooling on the counter" in restated
    assert "neighbour" not in restated


def test_restating_an_unfounded_claim_says_there_is_nothing(store):
    assert "nothing" in examine("a snake", []).restate().lower()


# ── the two axes, working together ───────────────────────────────────

@pytest.mark.parametrize("verdict,nature", [
    (Verdict.DEPENDENT, Nature.PARATANTRA),
    (Verdict.OVERLAID, Nature.PARIKALPITA),
    (Verdict.UNFOUNDED, Nature.PARIKALPITA),
])
def test_each_verdict_carries_a_nature(verdict, nature):
    assert Examination(claim="x", terms=(), supported=(), fabricated=(),
                       dependent=(), support=0.0, verdict=verdict).nature is nature


def test_the_nature_and_the_measure_distinguish_all_three(store):
    """三性 alone cannot tell overlaid from unfounded. 三量 supplies the rest."""
    g = grounds(store, "pizza")
    overlaid = examine("pizza from my neighbour", g)
    unfounded = examine("a snake", [])
    assert overlaid.nature is unfounded.nature is Nature.PARIKALPITA
    assert overlaid.measure is Pramana.ANUMANA
    assert unfounded.measure is Pramana.APRAMANA


# ── the examiners ────────────────────────────────────────────────────

def test_the_term_examiner_is_deliberately_literal(store):
    """It cannot see that "dark" follows from "luminance 0.02", and says so by
    over-reporting fabrication — the safe direction for a gate of this kind."""
    g = grounds(store, "frame 640×480 · luminance 0.02 · motion 0.00")
    assert examine("the room is dark", g).verdict is Verdict.UNFOUNDED


def test_a_model_examiner_may_see_what_the_literal_one_cannot(store):
    g = grounds(store, "frame 640×480 · luminance 0.02 · motion 0.00")

    class Fake:
        name = "fake"

        def converse(self, system, messages, tools):
            from alaya.providers import Response
            return Response(text='{"fabricated": [], "note": "low luminance is darkness"}')

    result = ModelExaminer(Fake()).examine("the room is dark", g)
    assert result.verdict is Verdict.DEPENDENT


def test_a_model_examiner_that_fails_falls_back_to_the_literal_one(store):
    g = grounds(store, "pizza")

    class Broken:
        name = "broken"

        def converse(self, system, messages, tools):
            raise RuntimeError("no model")

    result = ModelExaminer(Broken()).examine("pizza", g)
    assert result.verdict is Verdict.DEPENDENT


def test_examining_writes_nothing(store):
    g = grounds(store, "pizza")
    before = store.all()
    examine("pizza from my neighbour", g)
    TermExaminer().examine("anything at all", g)
    assert store.all() == before


def test_the_examination_renders_for_a_human(store):
    g = grounds(store, "pizza, cooling")
    text = examine("pizza left by my neighbour", g).render()
    assert "遍計所執" in text or "fabricated" in text.lower()
    assert "neighbour" in text


def test_the_residue_stays_readable_when_much_arose(store):
    """圓成實 is what remains *sayable*. A dump of forty grounds is not that."""
    g = grounds(store, *[f"a distinct thing number {i} happened" for i in range(12)])
    text = examine("a distinct thing happened, left by my neighbour", g).render()
    assert "and 8 more" in text
    assert text.count("distinct thing number") <= 8
