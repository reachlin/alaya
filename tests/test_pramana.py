"""三量 — how a cognition was reached, which is not the same as what it is about.

Phase 1 tagged every seed with 三性 alone. That conflates two axes the doctrine
keeps apart:

    三性  an ontology — what kind of thing this is (遍計 / 依他起 / 圓成實)
    三量  an epistemology — how it came to be known (現量 / 比量 / 非量)

They are orthogonal. A seed may be dependently arisen and still be known by a
mistaken cognition. 非量 is the doctrine's own name for the rope taken for a
snake, so the hallucination class belongs on this axis, not the other one.

前五識唯現量 — the five senses are direct perception only. 第六識通三量 — the
sixth is permeable to all three.
"""
import pytest

from alaya.seeds import Kind, Nature, Pramana, Seed, SeedError, Valence
from tests.conftest import percept as seed_of


def test_the_three_measures_exist():
    assert {p.value for p in Pramana} == {"pratyaksa", "anumana", "apramana"}


def test_a_percept_seed_is_direct_perception_by_default(store):
    """前五識唯現量 — the senses present; they do not infer and do not err."""
    with store.tick() as t:
        s = seed_of(t, "1.0s audio · rms 0.41")
    assert s.pramana is Pramana.PRATYAKSA


def test_a_percept_seed_may_not_claim_inference(store):
    with store.tick() as t:
        with pytest.raises(SeedError):
            t.perfume(
                content="someone is at the door", kind=Kind.PERCEPT,
                valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                pramana=Pramana.ANUMANA,
            )


def test_a_percept_seed_may_not_claim_error(store):
    """A sense cannot be wrong. Only discrimination can be wrong."""
    with store.tick() as t:
        with pytest.raises(SeedError):
            t.perfume(
                content="a snake", kind=Kind.PERCEPT,
                valence=Valence.NEUTRAL, nature=Nature.PARIKALPITA,
                pramana=Pramana.APRAMANA,
            )


def test_a_claim_may_be_reached_by_any_of_the_three(store):
    """第六識通三量 — the sixth consciousness ranges over all three measures.

    Seeing a coiled shape is 現量. Concluding "a rope, someone left it" is 比量.
    Recoiling from "a snake" is 非量. One and the same object, three cognitions
    of quite different standing — which is why the measure has to be recorded
    per claim rather than inferred from what the claim is about.
    """
    with store.tick() as t:
        root = seed_of(t, "a coiled shape on the path", conditions=("sense:eye",))

    with store.tick() as t:
        t.activate({"sense:eye"})
        reached = [
            t.perfume(
                content=f"a claim by {measure.value}", kind=Kind.CLAIM,
                valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                pramana=measure, parents=(root.id,),
            )
            for measure in Pramana
        ]
    assert [s.pramana for s in reached] == list(Pramana)


def test_pramana_is_part_of_the_content_address():
    common = dict(
        tick=1, at="t", kind=Kind.CLAIM, content="the rope",
        valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
    )
    direct = Seed.arise(pramana=Pramana.PRATYAKSA, **common)
    inferred = Seed.arise(pramana=Pramana.ANUMANA, **common)
    assert direct.id != inferred.id


def test_nature_and_pramana_are_independent(store):
    """A dependently-arisen thing can still be misapprehended."""
    with store.tick() as t:
        s = t.perfume(
            content="the rope is a snake", kind=Kind.CLAIM,
            valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA,      # the rope really is there
            pramana=Pramana.APRAMANA,      # but this cognition of it is false
        )
    assert s.nature is Nature.PARATANTRA
    assert s.pramana is Pramana.APRAMANA


def test_erroneous_cognitions_are_stored_without_objection(store):
    """無覆無記 — the store records 非量 as readily as 現量. Tagging is not refusing."""
    with store.tick() as t:
        s = t.perfume(
            content="a snake on the path", kind=Kind.CLAIM,
            valence=Valence.UNWHOLESOME, nature=Nature.PARIKALPITA,
            pramana=Pramana.APRAMANA,
        )
    assert store.get(s.id).pramana is Pramana.APRAMANA
