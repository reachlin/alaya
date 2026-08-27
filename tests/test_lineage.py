"""自类相续 — self-continuity, and the resolution of 刹那灭 against 恒随转.

A seed must perish every moment and yet persist until countered. The doctrine
resolves this by saying the seed does not endure and change: it perishes and
re-arises as one of its own kind. Taken as an implementation rule, that means
reinforcement is an append, never an update, and present strength is computed
from a whole lineage rather than stored on a row.
"""
import pytest

from alaya.seeds import Kind, LineageError, Nature, Valence
from tests.conftest import percept


def reinforce(tick, prior, content=None, **kw):
    return tick.perfume(
        content=content or prior.content,
        kind=Kind.PERCEPT,
        valence=prior.valence,
        nature=prior.nature,
        conditions=prior.conditions,
        parents=(prior.id,),
        lineage=prior.lineage,
        **kw,
    )


def test_reinforcement_appends_rather_than_updates(store):
    with store.tick() as t:
        first = percept(t, "the morning walk", conditions=("routine",))
    with store.tick() as t2:
        (prior,) = t2.activate({"routine"})
        again = reinforce(t2, prior)

    assert again.id != first.id
    assert again.lineage == first.lineage
    assert len(store.all()) == 2
    assert store.get(first.id) == first          # the prior arising is untouched


def test_reinforcement_strengthens_the_lineage(store):
    with store.tick() as t:
        first = percept(t, "the morning walk", conditions=("routine",))
    before = store.strength(first.lineage, now_tick=first.tick)

    with store.tick() as t2:
        (prior,) = t2.activate({"routine"})
        reinforce(t2, prior)
    after = store.strength(first.lineage, now_tick=first.tick + 1)

    assert after > before


def test_repeated_reinforcement_outweighs_decay(store):
    """A memory kept alive by recurrence stays strong; one left alone fades."""
    with store.tick() as t:
        kept = percept(t, "the morning walk", conditions=("routine",))
        left = percept(t, "a one-off errand", conditions=("errand",))

    for _ in range(8):
        with store.tick() as t2:
            (prior,) = t2.activate({"routine"})
            reinforce(t2, prior)

    now = store.tick_count
    assert store.strength(kept.lineage, now) > store.strength(left.lineage, now)


def test_why_a_memory_is_strong_is_answerable(store):
    """The whole point of appending: the reinforcement history survives."""
    with store.tick() as t:
        first = percept(t, "the morning walk", conditions=("routine",))
    for _ in range(3):
        with store.tick() as t2:
            (prior,) = t2.activate({"routine"})
            reinforce(t2, prior)

    chain = store.lineage(first.lineage)
    assert len(chain) == 4
    assert [s.tick for s in chain] == [1, 2, 3, 4]     # oldest first
    assert chain[0] == first


def test_activation_yields_the_current_arising_not_the_whole_chain(store):
    """A lineage fires as one seed — its present moment."""
    with store.tick() as t:
        percept(t, "the morning walk", conditions=("routine",))
    with store.tick() as t2:
        (prior,) = t2.activate({"routine"})
        latest = reinforce(t2, prior)
    with store.tick() as t3:
        active = t3.activate({"routine"})

    assert active == [latest]


def test_continuing_a_lineage_requires_a_parent_in_it(store):
    """自类相续 — continuity is of one kind with itself, not a jump between lines."""
    with store.tick() as t:
        a = percept(t, "the morning walk", conditions=("routine",))
        b = percept(t, "an unrelated thought", conditions=("idle",))

    with store.tick() as t2:
        t2.activate({"routine", "idle"})
        with pytest.raises(LineageError):
            t2.perfume(
                content="the morning walk",
                kind=Kind.PERCEPT, valence=Valence.NEUTRAL,
                nature=Nature.PARATANTRA,
                parents=(b.id,),          # not of this lineage
                lineage=a.lineage,
            )


def test_a_new_lineage_may_not_claim_an_unknown_root(store):
    with store.tick() as t:
        with pytest.raises(LineageError):
            t.perfume(
                content="orphan", kind=Kind.PERCEPT, valence=Valence.NEUTRAL,
                nature=Nature.PARATANTRA, lineage="0" * 64,
            )


def test_strength_of_an_unknown_lineage_is_zero(store):
    assert store.strength("0" * 64, now_tick=1) == 0.0
