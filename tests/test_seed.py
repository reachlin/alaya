"""The seed itself — 种子 as an immutable, content-addressed unit."""
import dataclasses

import pytest

from alaya.seeds import Kind, Nature, Seed, SeedError, Valence

AT = "2026-08-27T00:00:00+00:00"


def make(**kw):
    base = dict(
        tick=1,
        at=AT,
        kind=Kind.PERCEPT,
        content="rain on the window",
        valence=Valence.NEUTRAL,
        nature=Nature.PARATANTRA,
        conditions=("weather",),
        parents=(),
        weight=1.0,
    )
    base.update(kw)
    return Seed.arise(**base)


def test_seed_is_frozen():
    """刹那灭 — a seed has no mutable state to carry forward."""
    s = make()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.content = "changed"
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.weight = 99.0


def test_identical_fields_produce_identical_id():
    assert make().id == make().id


@pytest.mark.parametrize(
    "field,value",
    [
        ("content", "sun on the window"),
        ("tick", 2),
        ("at", "2026-08-27T00:00:01+00:00"),
        ("kind", Kind.CLAIM),
        ("valence", Valence.WHOLESOME),
        ("nature", Nature.PARIKALPITA),
        ("conditions", ("weather", "indoors")),
        ("weight", 0.5),
    ],
)
def test_any_field_change_changes_the_id(field, value):
    """The id is a content address over every field — nothing is outside it."""
    assert make().id != make(**{field: value}).id


def test_root_seed_is_its_own_lineage():
    """自类相续 begins with a seed that continues only itself."""
    s = make()
    assert s.lineage == s.id
    assert s.is_root


def test_conditions_and_parents_are_immutable_tuples():
    s = make(conditions=["a", "b"], parents=())
    assert isinstance(s.conditions, tuple)
    assert s.conditions == ("a", "b")


def test_conditions_are_order_independent_for_identity():
    """Conditions are a set of requirements, not a sequence."""
    assert make(conditions=("a", "b")).id == make(conditions=("b", "a")).id


def test_weight_must_be_positive():
    """恒随转 — strength decays toward a floor, it never starts at nothing."""
    with pytest.raises(SeedError):
        make(weight=0.0)
    with pytest.raises(SeedError):
        make(weight=-1.0)


def test_content_must_be_non_empty():
    with pytest.raises(SeedError):
        make(content="   ")


def test_derived_seed_requires_parents():
    """引自果 — a derived seed with no source is an effect without a cause."""
    with pytest.raises(SeedError):
        make(kind=Kind.DERIVED, parents=())


def test_round_trips_through_json():
    s = make(parents=("abc",), conditions=("weather", "dusk"))
    assert Seed.from_dict(s.to_dict()) == s


def test_json_round_trip_preserves_id():
    s = make()
    assert Seed.from_dict(s.to_dict()).id == s.id
