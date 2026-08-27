"""The store as 阿赖耶识 — 无覆无记, 恒转如瀑流.

Morally neutral: it never judges what it is given and never refuses it.
Continuously flowing: it is a file that only grows, and it survives reopening.
"""
import pytest

from alaya.seeds import Kind, Nature, SeedStore, Valence
from tests.conftest import percept


def test_the_store_survives_reopening(tmp_path):
    path = tmp_path / "seeds.jsonl"
    store = SeedStore(path)
    with store.tick() as t:
        a = percept(t, "before the restart", conditions=("session",))

    reopened = SeedStore(path)
    assert reopened.all() == (a,)
    assert reopened.get(a.id) == a
    assert reopened.tick_count == 1


def test_ticks_continue_across_reopening(tmp_path):
    """恒转如瀑流 — the stream does not restart because the process did."""
    path = tmp_path / "seeds.jsonl"
    store = SeedStore(path)
    with store.tick() as t:
        percept(t, "first")

    with SeedStore(path).tick() as t2:
        s = percept(t2, "second")
    assert s.tick == 2


def test_the_store_accepts_unwholesome_seeds_without_comment(store):
    """无覆无记 — the store is not a censor. Judgment belongs to a later layer."""
    with store.tick() as t:
        s = percept(t, "I lied about the deadline", valence=Valence.UNWHOLESOME)
    assert store.get(s.id).valence is Valence.UNWHOLESOME


def test_the_store_accepts_fabricated_seeds_without_comment(store):
    """A 遍计所执 seed is still a seed. Tagging it is not the same as refusing it."""
    with store.tick() as t:
        s = percept(t, "he must have meant it as an insult", nature=Nature.PARIKALPITA)
    assert store.get(s.id).nature is Nature.PARIKALPITA


def test_an_empty_store_is_empty_not_absent(store):
    assert store.all() == ()
    assert store.activate({"anything"}) == []
    assert store.recall("anything") == []
    assert store.tick_count == 0


def test_recall_matches_content(store):
    with store.tick() as t:
        rain = percept(t, "rain on the window", conditions=("weather",))
        percept(t, "a book left open", conditions=("desk",))
    assert store.recall("rain") == [rain]


def test_recall_ignores_conditions(store):
    """Recall is reading; activation is arising. They are different operations."""
    with store.tick() as t:
        s = percept(t, "the pier at low tide", conditions=("coast", "dusk"))
    assert store.activate({"coast"}) == []
    assert store.recall("pier") == [s]


def test_recall_is_case_insensitive(store):
    with store.tick() as t:
        s = percept(t, "Rain on the Window")
    assert store.recall("rain") == [s]


def test_recall_ranks_by_strength_and_honours_n(store):
    with store.tick() as t:
        faint = percept(t, "a note about tea", weight=0.1)
        loud = percept(t, "a shout about tea", weight=5.0)
        whisper = percept(t, "a whisper about tea", weight=0.5)
    assert store.recall("tea", n=2) == [loud, whisper]
    assert store.recall("tea") == [loud, whisper, faint]


def test_recall_with_no_query_returns_the_strongest(store):
    with store.tick() as t:
        percept(t, "quiet", weight=0.1)
        loud = percept(t, "loud", weight=9.0)
    assert store.recall(n=1) == [loud]


def test_recall_returns_the_current_arising_of_each_lineage(store):
    with store.tick() as t:
        first = percept(t, "the morning walk", conditions=("routine",))
    with store.tick() as t2:
        (prior,) = t2.activate({"routine"})
        latest = t2.perfume(
            content="the morning walk", kind=Kind.PERCEPT,
            valence=prior.valence, nature=prior.nature,
            conditions=prior.conditions, parents=(prior.id,), lineage=prior.lineage,
        )
    assert store.recall("morning") == [latest]
    assert first != latest


def test_get_of_an_unknown_id_raises(store):
    with pytest.raises(KeyError):
        store.get("0" * 64)


def test_the_file_is_line_delimited_json(store):
    with store.tick() as t:
        percept(t, "first")
        percept(t, "second")
    lines = store.path.read_text().strip().splitlines()
    assert len(lines) == 2
    assert all(line.startswith("{") and line.endswith("}") for line in lines)


def test_a_second_store_sees_what_the_first_wrote(tmp_path):
    path = tmp_path / "seeds.jsonl"
    with SeedStore(path).tick() as t:
        s = percept(t, "written by a")
    assert SeedStore(path).get(s.id) == s
