"""种子六义 — the six criteria, as executable invariants.

護法's six criteria for a valid seed are not commentary. Each one closes a hole,
and each one is a property of the store that can fail. This file is the
executable form of the table in DESIGN.md.
"""
import dataclasses

import pytest

from alaya.seeds import (
    Kind,
    Nature,
    ProvenanceError,
    Seed,
    SeedStore,
    SimultaneityError,
    TickClosedError,
    ValenceError,
    Valence,
)
from tests.conftest import percept


# ─────────────────────────────────────────────────────────────────────
# 一 · 刹那灭 — momentary. No abiding substance, therefore no mutation.
# ─────────────────────────────────────────────────────────────────────

def test_store_has_no_update_or_delete(store):
    """Not discouraged — the operations do not exist."""
    assert not hasattr(store, "update")
    assert not hasattr(store, "delete")
    assert not hasattr(store, "remove")
    assert not hasattr(store, "forget")


def test_seeds_returned_from_the_store_are_frozen(store):
    with store.tick() as t:
        percept(t, "a sound in the hallway")
    (s,) = store.all()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.weight = 5.0


def test_the_same_id_cannot_be_written_twice(store):
    """An id is an address. Rewriting it would be a seed that persisted and changed."""
    with store.tick() as t:
        s = percept(t, "a sound in the hallway")
    with pytest.raises(ProvenanceError):
        store._append(s)  # the only write path, exercised directly


def test_the_file_only_ever_grows(store):
    sizes = []
    for i in range(3):
        with store.tick() as t:
            percept(t, f"moment {i}")
        sizes.append(store.path.stat().st_size)
    assert sizes == sorted(sizes)
    assert len(set(sizes)) == 3


# ─────────────────────────────────────────────────────────────────────
# 二 · 果俱有 — seed and fruit are simultaneous, not sequential.
# ─────────────────────────────────────────────────────────────────────

def test_perfumed_seed_carries_the_current_tick(store):
    with store.tick() as t:
        s = percept(t, "first")
        assert s.tick == t.number
    with store.tick() as t2:
        s2 = percept(t2, "second")
    assert s2.tick == s.tick + 1


def test_parent_must_have_been_activated_in_this_same_tick(store):
    """The cause must be present with its fruit — 因果同时, not 因果异时."""
    with store.tick() as t:
        parent = percept(t, "the kettle is on", conditions=("kitchen",))

    with store.tick() as t2:
        # never activated in this tick — the cause is absent
        with pytest.raises(SimultaneityError):
            t2.perfume(
                content="tea is coming",
                kind=Kind.CLAIM,
                valence=Valence.NEUTRAL,
                nature=Nature.PARATANTRA,
                parents=(parent.id,),
            )


def test_parent_activated_in_this_tick_is_accepted(store):
    with store.tick() as t:
        parent = percept(t, "the kettle is on", conditions=("kitchen",))

    with store.tick() as t2:
        active = t2.activate({"kitchen"})
        assert [s.id for s in active] == [parent.id]
        child = t2.perfume(
            content="tea is coming",
            kind=Kind.CLAIM,
            valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA,
            parents=(parent.id,),
        )
    assert child.parents == (parent.id,)


def test_a_seed_perfumed_earlier_in_the_same_tick_may_be_a_parent(store):
    with store.tick() as t:
        first = percept(t, "footsteps")
        second = t.perfume(
            content="someone is home",
            kind=Kind.CLAIM,
            valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA,
            parents=(first.id,),
        )
    assert second.parents == (first.id,)
    assert second.tick == first.tick


def test_nothing_is_written_when_the_tick_raises(store):
    """The three moments commit together or not at all."""
    with pytest.raises(RuntimeError):
        with store.tick() as t:
            percept(t, "this should not survive")
            raise RuntimeError("the tick failed")
    assert store.all() == ()
    assert store.tick_count == 0


def test_perfuming_outside_a_tick_is_refused(store):
    with store.tick() as t:
        pass
    with pytest.raises(TickClosedError):
        percept(t, "too late")


# ─────────────────────────────────────────────────────────────────────
# 三 · 恒随转 — continuous until countered. Decay, never deletion.
# ─────────────────────────────────────────────────────────────────────

def test_strength_decays_with_distance_in_ticks(store):
    with store.tick() as t:
        s = percept(t, "a bright afternoon")
    near = store.strength(s.lineage, now_tick=s.tick)
    far = store.strength(s.lineage, now_tick=s.tick + 500)
    assert far < near


def test_strength_never_reaches_zero(store):
    """A forgotten seed is a quiet one, not an absent one."""
    with store.tick() as t:
        s = percept(t, "a bright afternoon")
    assert store.strength(s.lineage, now_tick=s.tick + 10_000_000) > 0


def test_a_faded_seed_is_still_present_and_still_activates(store):
    with store.tick() as t:
        s = percept(t, "a bright afternoon", conditions=("weather",))
    assert s in store.all()
    assert store.activate({"weather"}, now_tick=s.tick + 10_000) == [s]


# ─────────────────────────────────────────────────────────────────────
# 四 · 性决定 — determinate nature. A wholesome seed cannot bear bitter fruit.
# ─────────────────────────────────────────────────────────────────────

def test_valence_is_fixed_at_write_and_survives_retrieval(store):
    with store.tick() as t:
        s = percept(t, "she thanked him", valence=Valence.WHOLESOME, conditions=("social",))
    with store.tick() as t2:
        (again,) = t2.activate({"social"})
    assert again.valence is Valence.WHOLESOME
    assert store.get(s.id).valence is Valence.WHOLESOME


def test_a_derived_seed_cannot_invert_its_parents_valence(store):
    """各引自类之果 — the fruit is of the same kind as the seed."""
    with store.tick() as t:
        good = percept(t, "she thanked him", valence=Valence.WHOLESOME, conditions=("social",))
    with store.tick() as t2:
        t2.activate({"social"})
        with pytest.raises(ValenceError):
            t2.perfume(
                content="she was being sarcastic",
                kind=Kind.DERIVED,
                valence=Valence.UNWHOLESOME,
                nature=Nature.PARIKALPITA,
                parents=(good.id,),
            )


def test_a_derived_seed_of_like_valence_is_accepted(store):
    with store.tick() as t:
        good = percept(t, "she thanked him", valence=Valence.WHOLESOME, conditions=("social",))
    with store.tick() as t2:
        t2.activate({"social"})
        d = t2.perfume(
            content="he is welcome here",
            kind=Kind.DERIVED,
            valence=Valence.WHOLESOME,
            nature=Nature.PARATANTRA,
            parents=(good.id,),
        )
    assert d.valence is Valence.WHOLESOME


def test_non_derived_seeds_may_hold_any_valence(store):
    """Only 种子生种子 is bound by like-kind. A fresh act may be judged freshly."""
    with store.tick() as t:
        good = percept(t, "she thanked him", valence=Valence.WHOLESOME, conditions=("social",))
    with store.tick() as t2:
        t2.activate({"social"})
        act = t2.perfume(
            content="he ignored her",
            kind=Kind.ACT,
            valence=Valence.UNWHOLESOME,
            nature=Nature.PARATANTRA,
            parents=(good.id,),
        )
    assert act.valence is Valence.UNWHOLESOME


# ─────────────────────────────────────────────────────────────────────
# 五 · 待众缘 — awaits conditions. Presence in the store is not activation.
# ─────────────────────────────────────────────────────────────────────

def test_a_seed_does_not_fire_when_its_conditions_are_absent(store):
    with store.tick() as t:
        percept(t, "the pier at low tide", conditions=("coast", "dusk"))
    assert store.activate({"coast"}) == []
    assert store.activate(set()) == []


def test_a_seed_fires_when_every_condition_is_present(store):
    with store.tick() as t:
        s = percept(t, "the pier at low tide", conditions=("coast", "dusk"))
    assert store.activate({"coast", "dusk"}) == [s]
    assert store.activate({"coast", "dusk", "cold"}) == [s]


def test_an_unconditioned_seed_always_fires(store):
    with store.tick() as t:
        s = percept(t, "I am here", conditions=())
    assert store.activate(set()) == [s]
    assert store.activate({"anything"}) == [s]


def test_stored_but_unfired_seeds_are_still_stored(store):
    with store.tick() as t:
        s = percept(t, "the pier at low tide", conditions=("coast", "dusk"))
    assert store.activate({"coast"}) == []
    assert store.get(s.id) == s


def test_activation_is_ordered_by_strength(store):
    with store.tick() as t:
        weak = percept(t, "a passing car", conditions=("street",), weight=0.2)
        strong = percept(t, "a siren", conditions=("street",), weight=3.0)
    assert store.activate({"street"}) == [strong, weak]


# ─────────────────────────────────────────────────────────────────────
# 六 · 引自果 — produces its own fruit. Provenance is total.
# ─────────────────────────────────────────────────────────────────────

def test_an_unknown_parent_is_refused(store):
    with store.tick() as t:
        with pytest.raises(ProvenanceError):
            t.perfume(
                content="a conclusion from nowhere",
                kind=Kind.CLAIM,
                valence=Valence.NEUTRAL,
                nature=Nature.PARATANTRA,
                parents=("0" * 64,),
            )


def test_trace_returns_the_full_ancestry(store):
    with store.tick() as t:
        a = percept(t, "footsteps", conditions=("home",))
        b = t.perfume(
            content="someone is home",
            kind=Kind.CLAIM, valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA, parents=(a.id,),
        )
    with store.tick() as t2:
        t2.activate({"home"})
        c = t2.perfume(
            content="I said hello",
            kind=Kind.ACT, valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA, parents=(b.id,),
        )
    chain = store.trace(c.id)
    assert [s.id for s in chain] == [c.id, b.id, a.id]


def test_trace_of_a_root_is_just_itself(store):
    with store.tick() as t:
        a = percept(t, "footsteps")
    assert store.trace(a.id) == [a]


def test_trace_visits_a_shared_ancestor_once(store):
    with store.tick() as t:
        root = percept(t, "a shared origin")
        left = t.perfume(content="left", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                         nature=Nature.PARATANTRA, parents=(root.id,))
        right = t.perfume(content="right", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                          nature=Nature.PARATANTRA, parents=(root.id,))
        joined = t.perfume(content="both", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                           nature=Nature.PARATANTRA, parents=(left.id, right.id))
    ids = [s.id for s in store.trace(joined.id)]
    assert ids.count(root.id) == 1
    assert set(ids) == {joined.id, left.id, right.id, root.id}


def test_every_act_is_attributable_to_the_seeds_that_produced_it(store):
    """The claim the whole store exists to support."""
    with store.tick() as t:
        heard = percept(t, "the user said they were cold", conditions=("user",))
    with store.tick() as t2:
        active = t2.activate({"user"})
        act = t2.perfume(
            content="closed the window",
            kind=Kind.ACT, valence=Valence.WHOLESOME,
            nature=Nature.PARATANTRA, parents=[s.id for s in active],
        )
    assert heard in store.trace(act.id)


def test_ancestry_reports_true_causal_depth(store):
    """A provenance display that misrepresents structure is worse than none.

    ``trace`` is a flat list in breadth-first order; indenting by position in
    that list draws a tree that is not the causal graph. ``ancestry`` carries
    the real depth so a renderer cannot invent one.
    """
    with store.tick() as t:
        root = percept(t, "a shared origin")
        left = t.perfume(content="left", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                         nature=Nature.PARATANTRA, parents=(root.id,))
        right = t.perfume(content="right", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                          nature=Nature.PARATANTRA, parents=(root.id,))
        joined = t.perfume(content="both", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                           nature=Nature.PARATANTRA, parents=(left.id, right.id))

    depths = {seed.id: depth for depth, seed in store.ancestry(joined.id)}
    assert depths[joined.id] == 0
    assert depths[left.id] == depths[right.id] == 1
    assert depths[root.id] == 2


def test_ancestry_gives_a_shared_ancestor_its_shallowest_depth(store):
    """A cause reached by two routes is as near as its nearest route."""
    with store.tick() as t:
        root = percept(t, "a shared origin")
        mid = t.perfume(content="middle", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                        nature=Nature.PARATANTRA, parents=(root.id,))
        both = t.perfume(content="both", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                         nature=Nature.PARATANTRA, parents=(root.id, mid.id))
    depths = {seed.id: depth for depth, seed in store.ancestry(both.id)}
    assert depths[root.id] == 1


def test_ancestry_and_trace_cover_the_same_seeds(store):
    with store.tick() as t:
        a = percept(t, "footsteps")
        b = t.perfume(content="someone is home", kind=Kind.CLAIM, valence=Valence.NEUTRAL,
                      nature=Nature.PARATANTRA, parents=(a.id,))
    assert [s for _, s in store.ancestry(b.id)] == store.trace(b.id)
