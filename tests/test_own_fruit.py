"""引自果 — 各引自類之果，色心不相互生.

Phase 1 read this criterion as "provenance is traceable", which is not what it
says. 引自果 is a *determinacy* rule, the sibling of 性決定: a seed produces
fruit of its own category. A form-seed yields form and a mind-seed yields mind;
they do not cross.

Traceability is a real property of this store, but it follows from 果俱有
recording the causal link — it is not this criterion.
"""
import pytest

from alaya.seeds import Kind, KindError, Nature, Valence
from tests.conftest import percept as seed_of


def test_a_lineage_continues_as_its_own_kind(store):
    with store.tick() as t:
        first = seed_of(t, "the morning walk", conditions=("routine",))
    with store.tick() as t:
        (prior,) = t.activate({"routine"})
        again = t.perfume(
            content="the morning walk", kind=Kind.PERCEPT,
            valence=prior.valence, nature=prior.nature,
            conditions=prior.conditions, parents=(prior.id,), lineage=prior.lineage,
        )
    assert again.kind is first.kind


def test_a_lineage_may_not_change_its_kind(store):
    """色心不相互生 — a line of perception does not become a line of action."""
    with store.tick() as t:
        first = seed_of(t, "the morning walk", conditions=("routine",))
    with store.tick() as t:
        (prior,) = t.activate({"routine"})
        with pytest.raises(KindError):
            t.perfume(
                content="went for the walk", kind=Kind.ACT,
                valence=prior.valence, nature=prior.nature,
                conditions=prior.conditions, parents=(prior.id,), lineage=prior.lineage,
            )


def test_a_derived_seed_may_not_mix_categories(store):
    """种子生种子 draws on one category, not a blend of incompatible ones."""
    with store.tick() as t:
        heard = seed_of(t, "a rising tone", conditions=("c",))
        did = t.perfume(content="poured the tea", kind=Kind.ACT,
                        valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                        conditions=("c",))
    with store.tick() as t:
        t.activate({"c"})
        with pytest.raises(KindError):
            t.perfume(
                content="tea happens when kettles whistle", kind=Kind.DERIVED,
                valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                parents=(heard.id, did.id),
            )


def test_a_derived_seed_from_one_category_is_accepted(store):
    with store.tick() as t:
        a = seed_of(t, "a rising tone", conditions=("c",))
        b = seed_of(t, "a second rising tone", conditions=("c",))
    with store.tick() as t:
        t.activate({"c"})
        d = t.perfume(
            content="tones rise before the boil", kind=Kind.DERIVED,
            valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
            parents=(a.id, b.id),
        )
    assert d.kind is Kind.DERIVED


def test_a_new_lineage_may_be_of_any_kind(store):
    """The rule binds continuation and derivation, not fresh arising."""
    with store.tick() as t:
        heard = seed_of(t, "a rising tone", conditions=("c",))
    with store.tick() as t:
        t.activate({"c"})
        act = t.perfume(content="poured the tea", kind=Kind.ACT,
                        valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                        parents=(heard.id,))
    assert act.kind is Kind.ACT and act.is_root
