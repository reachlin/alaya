"""第七末那識 — 恆審思量.

Manas takes the 見分 of the store — the *activity* of knowing — and reads it as
a knower. That misreading is not a bug to be removed: it is what gives an agent
a continuous self at all. What the doctrine demands, and what this module
provides, is that the distortion be *measurable*. 平等性智 is the metric on it,
not its deletion.
"""
from alaya.manas import BiasReport, Manas
from alaya.seeds import Kind, Nature, Valence
from tests.conftest import percept as seed_of


def act(t, content, valence=Valence.NEUTRAL, parents=()):
    return t.perfume(content=content, kind=Kind.ACT, valence=valence,
                     nature=Nature.PARATANTRA, parents=parents)


# ── the self-model ───────────────────────────────────────────────────

def test_a_fresh_manas_has_a_provisional_self(tmp_path, store):
    m = Manas(store, path=tmp_path / "manas.md")
    assert m.self_model.strip()


def test_the_self_model_persists(tmp_path, store):
    path = tmp_path / "manas.md"
    Manas(store, path=path).revise("I am the one who waits by the door.")
    assert "waits by the door" in Manas(store, path=path).self_model


def test_colour_carries_the_self_model_into_every_prompt(tmp_path, store):
    m = Manas(store, path=tmp_path / "manas.md")
    m.revise("I am the one who waits by the door.")
    assert "waits by the door" in m.color()


def test_colour_admits_that_it_is_a_construction(tmp_path, store):
    """The agent is told, in the prompt, that its self is manas — not a fact."""
    m = Manas(store, path=tmp_path / "manas.md")
    text = m.color().lower()
    assert "manas" in text
    assert "construction" in text or "constructed" in text


# ── 緣第八識見分 — what it appropriates ──────────────────────────────

def test_appropriation_reads_the_store_not_the_self_model(tmp_path, store):
    with store.tick() as t:
        seed_of(t, "the porch light", conditions=("sense:eye",))
        seed_of(t, "the gate latch", conditions=("sense:eye",))
        seed_of(t, "a rising tone", conditions=("sense:ear",))
    m = Manas(store, path=tmp_path / "manas.md")
    a = m.appropriate()
    assert a.top_conditions[0][0] == "sense:eye"
    assert a.seed_count == 3


def test_appropriation_of_an_empty_store_is_empty_not_an_error(tmp_path, store):
    a = Manas(store, path=tmp_path / "manas.md").appropriate()
    assert a.seed_count == 0
    assert a.top_conditions == ()


# ── the audit — 平等性智 as a measurement ────────────────────────────

def test_a_narrow_attention_scores_as_concentrated(tmp_path, store):
    with store.tick() as t:
        for i in range(8):
            seed_of(t, f"the porch light, again ({i})", conditions=("sense:eye",))
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.attention_concentration > 0.9


def test_a_broad_attention_scores_as_dispersed(tmp_path, store):
    with store.tick() as t:
        for i, cond in enumerate(["a", "b", "c", "d", "e", "f", "g", "h"]):
            seed_of(t, f"note {i}", conditions=(cond,))
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.attention_concentration < 0.2


def test_self_reference_is_counted(tmp_path, store):
    with store.tick() as t:
        act(t, "I decided I would wait")
        act(t, "I said I was fine")
        act(t, "the gate was open")
        act(t, "rain started")
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert 0.4 <= report.self_reference <= 0.6


def test_valence_skew_is_reported(tmp_path, store):
    with store.tick() as t:
        act(t, "helped", valence=Valence.WHOLESOME)
        act(t, "helped again", valence=Valence.WHOLESOME)
        act(t, "helped once more", valence=Valence.WHOLESOME)
        act(t, "snapped at them", valence=Valence.UNWHOLESOME)
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.valence_skew[Valence.WHOLESOME] == 0.75
    assert report.valence_skew[Valence.UNWHOLESOME] == 0.25


def test_repetition_notices_an_agent_going_over_old_ground(tmp_path, store):
    with store.tick() as t:
        first = seed_of(t, "the morning walk", conditions=("routine",))
    for _ in range(5):
        with store.tick() as t:
            (prior,) = t.activate({"routine"})
            t.perfume(content="the morning walk", kind=Kind.PERCEPT,
                      valence=prior.valence, nature=prior.nature,
                      conditions=prior.conditions, parents=(prior.id,),
                      lineage=prior.lineage)
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.repetition > 0.7


def test_an_audit_of_a_varied_store_flags_nothing(tmp_path, store):
    with store.tick() as t:
        for i, cond in enumerate("abcdefgh"):
            seed_of(t, f"a distinct moment {i}", conditions=(cond,))
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.notes == ()


def test_an_audit_of_a_fixated_store_says_so(tmp_path, store):
    with store.tick() as t:
        for i in range(8):
            act(t, f"I thought about myself again ({i})")
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert report.notes


def test_the_audit_writes_nothing(tmp_path, store):
    """Measuring the distortion must not add to it."""
    with store.tick() as t:
        act(t, "I did a thing")
    before = store.all()
    Manas(store, path=tmp_path / "manas.md").audit()
    assert store.all() == before


def test_the_audit_renders_for_a_human(tmp_path, store):
    with store.tick() as t:
        act(t, "I did a thing")
    text = Manas(store, path=tmp_path / "manas.md").audit().render()
    assert "concentration" in text.lower()
    assert "%" in text


def test_an_audit_of_an_empty_store_is_neutral(tmp_path, store):
    report = Manas(store, path=tmp_path / "manas.md").audit()
    assert isinstance(report, BiasReport)
    assert report.self_reference == 0.0
    assert report.notes == ()
