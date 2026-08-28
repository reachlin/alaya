"""種子生種子 — seeds producing seeds, without anything being destroyed.

The third causal moment. 種子生現行 and 現行熏種子 both cross between latent and
manifest; this one stays entirely within the store: 自類相續, a line of seeds
succeeding itself.

Consolidation is what an agent needs after long running — fifty near-identical
memories should become one thing that arises, not fifty. But the store's own
invariants forbid the obvious implementation:

    剎那滅  you cannot edit the fifty into one
    恆隨轉  you cannot delete the forty-nine

So consolidation must be **additive**: read the cluster, and perfume a new
DERIVED seed that abstracts it. The originals stay exactly where they are,
quietly, and the abstraction is what fires.

果俱有 then forces one more thing, and it is the elegant part: to cite the
fifty as parents, they must be *present* — so the consolidator has to make them
arise first. You cannot abstract from memories you have not actually recalled.
"""
import pytest

from alaya.seeds import Kind, Nature, Valence
from alaya.seeds.consolidate import Cluster, cluster, consolidate
from tests.conftest import percept as seed_of


def claim(t, content, valence=Valence.NEUTRAL, conditions=()):
    return t.perfume(content=content, kind=Kind.CLAIM, valence=valence,
                     nature=Nature.PARATANTRA, conditions=conditions)


# ── clustering ───────────────────────────────────────────────────────

def test_near_duplicates_cluster(store):
    with store.tick() as t:
        a = seed_of(t, "the kettle whistled in the kitchen")
        b = seed_of(t, "the kettle whistled again in the kitchen")
    (group,) = cluster([a, b])
    assert set(group.seeds) == {a, b}


def test_unrelated_content_does_not_cluster(store):
    with store.tick() as t:
        a = seed_of(t, "the kettle whistled in the kitchen")
        b = seed_of(t, "a bicycle passed the window")
    assert cluster([a, b]) == []


def test_kinds_never_cluster_together(store):
    """引自果 — 色心不相互生. A derived seed drawn from a mixture is refused,
    so the clustering must never propose one."""
    with store.tick() as t:
        a = seed_of(t, "the kettle whistled in the kitchen")
        b = claim(t, "the kettle whistled in the kitchen")
    assert cluster([a, b]) == []


def test_valences_never_cluster_together(store):
    """性決定 — a wholesome line and an unwholesome one are different lines."""
    with store.tick() as t:
        a = claim(t, "she thanked him warmly today", valence=Valence.WHOLESOME)
        b = claim(t, "she thanked him warmly again", valence=Valence.UNWHOLESOME)
    assert cluster([a, b]) == []


def test_a_lone_seed_is_not_a_cluster(store):
    with store.tick() as t:
        a = seed_of(t, "the kettle whistled in the kitchen")
    assert cluster([a]) == []


def test_clustering_is_pure(store):
    with store.tick() as t:
        a = seed_of(t, "the kettle whistled in the kitchen")
        b = seed_of(t, "the kettle whistled again in the kitchen")
    before = store.all()
    cluster([a, b])
    assert store.all() == before


# ── consolidating ────────────────────────────────────────────────────

def _redundant(store, n=4):
    with store.tick() as t:
        return [seed_of(t, f"the kettle whistled in the kitchen, time {i}",
                        conditions=("sense:ear", "room:kitchen"))
                for i in range(n)]


def test_consolidation_produces_a_derived_seed(store):
    _redundant(store)
    (derived,) = consolidate(store)
    assert derived.kind is Kind.DERIVED


def test_the_abstraction_cites_the_seeds_it_came_from(store):
    """引自果's record: you can always ask what an abstraction abstracted."""
    members = _redundant(store)
    (derived,) = consolidate(store)
    assert set(derived.parents) == {m.id for m in members}
    traced = store.trace(derived.id)
    assert all(m in traced for m in members)


def test_nothing_is_removed_by_consolidating(store):
    """恆隨轉 — the forty-nine stay. They simply stop being what arises."""
    members = _redundant(store)
    before = len(store.all())
    consolidate(store)
    assert len(store.all()) == before + 1
    assert all(m in store.all() for m in members)


def test_the_abstraction_keeps_the_valence_of_its_members(store):
    with store.tick() as t:
        for i in range(3):
            claim(t, f"she thanked him warmly, time {i}", valence=Valence.WHOLESOME,
                  conditions=("social",))
    (derived,) = consolidate(store)
    assert derived.valence is Valence.WHOLESOME


def test_the_abstraction_fires_wherever_its_members_would(store):
    """Conditions are the intersection: the fewest requirements, so the
    abstraction arises in every situation any member would have arisen in."""
    with store.tick() as t:
        seed_of(t, "the kettle whistled in the kitchen once",
                conditions=("sense:ear", "room:kitchen", "time:morning"))
        seed_of(t, "the kettle whistled in the kitchen twice",
                conditions=("sense:ear", "room:kitchen", "time:evening"))
    (derived,) = consolidate(store)
    assert set(derived.conditions) == {"sense:ear", "room:kitchen"}


def test_the_abstraction_says_what_it_abstracted(store):
    _redundant(store, n=5)
    (derived,) = consolidate(store)
    assert "kettle" in derived.content
    assert "5" in derived.content


def test_abstractions_are_not_themselves_re_abstracted(store):
    """One pass of 種子生種子 per turning. Abstracting abstractions compounds
    whatever the first pass got wrong."""
    _redundant(store)
    assert len(consolidate(store)) == 1
    assert consolidate(store) == []


def test_consolidating_an_empty_store_does_nothing(store):
    assert consolidate(store) == []


def test_consolidating_a_store_with_nothing_redundant_does_nothing(store):
    with store.tick() as t:
        seed_of(t, "the kettle whistled")
        seed_of(t, "a bicycle passed the window")
        seed_of(t, "someone laughed downstairs")
    assert consolidate(store) == []


def test_only_the_current_arising_of_a_lineage_is_consolidated(store):
    """果俱有 — a superseded arising cannot be made present, so it cannot be
    cited. The consolidator must work on what can actually arise."""
    with store.tick() as t:
        first = seed_of(t, "the kettle whistled in the kitchen", conditions=("c",))
    with store.tick() as t:
        (prior,) = t.activate({"c"})
        t.perfume(content="the kettle whistled in the kitchen", kind=Kind.PERCEPT,
                  valence=prior.valence, nature=prior.nature,
                  conditions=prior.conditions, parents=(prior.id,), lineage=prior.lineage)
    with store.tick() as t:
        seed_of(t, "the kettle whistled in the kitchen anew", conditions=("c",))

    (derived,) = consolidate(store)
    assert first.id not in derived.parents


def test_consolidation_respects_a_limit(store):
    with store.tick() as t:
        for i in range(3):
            seed_of(t, f"the kettle whistled in the kitchen {i}", conditions=("a",))
        for i in range(3):
            seed_of(t, f"a bicycle passed the window slowly {i}", conditions=("b",))
    assert len(consolidate(store, limit=1)) == 1
