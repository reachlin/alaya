"""轉識成智 — the transformation of consciousness into wisdom.

Not the extinction of the eight layers. 轉依 (āśraya-parāvṛtti) is a
transformation of the *basis*: the same faculties, no longer running on
自我 as their organising principle. Each consciousness becomes a wisdom:

    前五識 → 成所作智   accomplishing what is to be done
    第六識 → 妙觀察智   observing particulars without obstruction
    第七識 → 平等性智   seeing self and other as equal
    第八識 → 大圓鏡智   reflecting everything without distortion

And they do not turn together. 六七因中轉，五八果上圓 — the sixth and seventh
turn *in the cause*, at 見道, while practice is still under way; the five and
the eighth are perfected only *at the fruit*. The doctrine's reason is that
分別 and 我執 are reachable by wisdom directly, while the sense faculties and
the store cannot be corrected from inside their own operation.

Read as engineering that is simply the right split: prompt and self-model are
cheap and can be revised from the agent's own trace while it runs; sensors and
substrate need the stream stopped and a batch pass. This module enforces it —
a 果上圓 turning attempted mid-tick raises, because it cannot see a consistent
store while one is being written.
"""
import pytest

from alaya.directive import Directive
from alaya.manas import Manas
from alaya.seeds import Kind, Nature, Pramana, Valence
from alaya.senses import DormantFaculty, Ear, Sense, SenseField
from alaya.wisdom import (
    Accomplishing,
    Basis,
    Discerning,
    Equality,
    Mirror,
    Stage,
    UntimelyError,
    measure,
    turn,
)
from tests.conftest import percept as seed_of


def basis_of(store, tmp_path, senses=None):
    return Basis(
        store=store,
        manas=Manas(store, path=tmp_path / "manas.md"),
        directive=Directive(tmp_path / "directive.md"),
        senses=senses,
    )


def claim(t, content, nature=Nature.PARATANTRA, pramana=Pramana.ANUMANA, **kw):
    return t.perfume(content=content, kind=Kind.CLAIM,
                     valence=kw.pop("valence", Valence.NEUTRAL),
                     nature=nature, pramana=pramana, **kw)


# ── the four, and when each turns ────────────────────────────────────

def test_the_four_wisdoms_name_their_layers():
    assert Discerning().layer == "第六意識" and Discerning().wisdom == "妙觀察智"
    assert Equality().layer == "第七末那識" and Equality().wisdom == "平等性智"
    assert Accomplishing().layer == "前五識" and Accomplishing().wisdom == "成所作智"
    assert Mirror().layer == "第八阿賴耶識" and Mirror().wisdom == "大圓鏡智"


def test_六七因中轉():
    assert Discerning().stage is Stage.CAUSE
    assert Equality().stage is Stage.CAUSE


def test_五八果上圓():
    assert Accomplishing().stage is Stage.FRUIT
    assert Mirror().stage is Stage.FRUIT


def test_a_cause_turning_runs_only_the_sixth_and_seventh(store, tmp_path):
    result = turn(basis_of(store, tmp_path), stage=Stage.CAUSE)
    assert {p.wisdom for p in result.progress} == {"妙觀察智", "平等性智"}


def test_a_fruit_turning_runs_only_the_five_and_the_eighth(store, tmp_path):
    result = turn(basis_of(store, tmp_path), stage=Stage.FRUIT)
    assert {p.wisdom for p in result.progress} == {"成所作智", "大圓鏡智"}


def test_a_fruit_turning_is_refused_while_the_stream_is_running(store, tmp_path):
    """果上圓 — it cannot be done from inside the operation it is correcting."""
    basis = basis_of(store, tmp_path)
    with store.tick():
        with pytest.raises(UntimelyError):
            turn(basis, stage=Stage.FRUIT)


def test_a_cause_turning_is_allowed_while_the_stream_is_running(store, tmp_path):
    """因中轉 — revisable during practice, which is the whole point of it."""
    basis = basis_of(store, tmp_path)
    with store.tick():
        assert turn(basis, stage=Stage.CAUSE).progress


def test_measuring_covers_all_four_and_changes_nothing(store, tmp_path):
    with store.tick() as t:
        claim(t, "something happened")
    basis = basis_of(store, tmp_path)
    before = store.all()
    result = measure(basis)
    assert len(result.progress) == 4
    assert all(not p.changed for p in result.progress)
    assert store.all() == before


def test_measuring_is_allowed_mid_stream_even_for_fruit_wisdoms(store, tmp_path):
    """Looking is not turning. 果上圓 restricts the transformation, not the metric."""
    basis = basis_of(store, tmp_path)
    with store.tick():
        assert len(measure(basis).progress) == 4


# ── 妙觀察智 — the sixth ─────────────────────────────────────────────

def test_a_store_full_of_fabrication_scores_low(store, tmp_path):
    with store.tick() as t:
        for i in range(6):
            claim(t, f"someone is at the door {i}", nature=Nature.PARIKALPITA,
                  pramana=Pramana.APRAMANA)
    assert Discerning().measure(basis_of(store, tmp_path)).score < 0.3


def test_a_store_of_grounded_claims_scores_high(store, tmp_path):
    with store.tick() as t:
        for i in range(6):
            claim(t, f"the kettle whistled {i}")
    assert Discerning().measure(basis_of(store, tmp_path)).score > 0.9


def test_turning_the_sixth_writes_a_directive_naming_the_problem(store, tmp_path):
    with store.tick() as t:
        for i in range(6):
            claim(t, f"my neighbour left this {i}", nature=Nature.PARIKALPITA,
                  pramana=Pramana.APRAMANA)
    basis = basis_of(store, tmp_path)
    progress = Discerning().turn(basis)
    assert progress.changed
    assert "examine" in basis.directive.read().lower()


def test_the_directive_names_what_keeps_being_made_up(store, tmp_path):
    with store.tick() as t:
        for i in range(5):
            claim(t, f"my neighbour left this {i}", nature=Nature.PARIKALPITA)
    basis = basis_of(store, tmp_path)
    Discerning().turn(basis)
    assert "neighbour" in basis.directive.read()


def test_a_clean_store_gets_an_encouraging_directive_not_a_scolding(store, tmp_path):
    with store.tick() as t:
        for i in range(6):
            claim(t, f"the kettle whistled {i}")
    basis = basis_of(store, tmp_path)
    Discerning().turn(basis)
    assert "borne" in basis.directive.read().lower()


# ── 平等性智 — the seventh ───────────────────────────────────────────

def test_a_self_absorbed_store_scores_low(store, tmp_path):
    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I thought about myself again {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    assert Equality().measure(basis_of(store, tmp_path)).score < 0.5


def test_a_balanced_store_scores_high(store, tmp_path):
    with store.tick() as t:
        for i, c in enumerate("abcdefgh"):
            t.perfume(content=f"the light changed on the wall {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=(c,))
    assert Equality().measure(basis_of(store, tmp_path)).score > 0.7


def test_turning_the_seventh_revises_the_self_model(store, tmp_path):
    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I did this myself, again {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    basis = basis_of(store, tmp_path)
    basis.manas.revise("I am the one who waits by the door.")
    progress = Equality().turn(basis)
    assert progress.changed
    assert "平等性智" in basis.manas.self_model


def test_the_original_self_account_survives_the_correction(store, tmp_path):
    """轉依 transforms the basis. It does not replace the person."""
    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I did this myself {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    basis = basis_of(store, tmp_path)
    basis.manas.revise("I am the one who waits by the door.")
    Equality().turn(basis)
    assert "waits by the door" in basis.manas.self_model


def test_turning_the_seventh_twice_does_not_stack_corrections(store, tmp_path):
    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I did this myself {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    basis = basis_of(store, tmp_path)
    basis.manas.revise("I am the one who waits by the door.")
    Equality().turn(basis)
    Equality().turn(basis)
    assert basis.manas.self_model.count("平等性智") == 1


# ── 成所作智 — the five ──────────────────────────────────────────────

def test_the_fifth_reports_what_each_faculty_contributed(store, tmp_path):
    with store.tick() as t:
        ear = seed_of(t, "a rising tone", conditions=("sense:ear",))
        seed_of(t, "pizza", conditions=("sense:nose",))
    with store.tick() as t:
        t.activate({"sense:ear"})
        t.perfume(content="checked the kettle", kind=Kind.ACT, valence=Valence.NEUTRAL,
                  nature=Nature.PARATANTRA, parents=(ear.id,))

    progress = Accomplishing().measure(basis_of(store, tmp_path))
    assert progress.metrics["yield"]["ear"] == 1.0
    assert progress.metrics["yield"]["nose"] == 0.0


def test_the_fifth_notices_a_faculty_that_never_grounds_anything(store, tmp_path):
    with store.tick() as t:
        for i in range(4):
            seed_of(t, f"1.0s audio · silence (rms 0.00{i})",
                    conditions=("sense:ear", "level:silent"))
    progress = Accomplishing().measure(basis_of(store, tmp_path))
    assert any("ear" in n for n in progress.notes)


def test_turning_the_fifth_recalibrates_an_ear_that_hears_only_silence(store, tmp_path):
    """成所作智 — the faculty itself is adjusted, which cannot be done mid-tick."""
    ear = Ear(recorder=lambda: None, gate=0.05)
    senses = SenseField(faculties={Sense.EAR: ear})
    with store.tick() as t:
        for i in range(10):
            seed_of(t, f"silence {i}", conditions=("sense:ear", "level:silent"))

    progress = Accomplishing().turn(basis_of(store, tmp_path, senses=senses))
    assert ear.gate < 0.05
    assert progress.changed


def test_turning_the_fifth_without_a_sense_field_only_reports(store, tmp_path):
    with store.tick() as t:
        seed_of(t, "a rising tone", conditions=("sense:ear",))
    assert Accomplishing().turn(basis_of(store, tmp_path)).changed is False


# ── 大圓鏡智 — the eighth ────────────────────────────────────────────

def test_a_redundant_store_scores_low(store, tmp_path):
    with store.tick() as t:
        for i in range(6):
            seed_of(t, f"the kettle whistled in the kitchen, time {i}",
                    conditions=("sense:ear",))
    assert Mirror().measure(basis_of(store, tmp_path)).score < 0.5


def test_a_varied_store_scores_high(store, tmp_path):
    with store.tick() as t:
        seed_of(t, "the kettle whistled")
        seed_of(t, "a bicycle passed the window")
        seed_of(t, "someone laughed downstairs")
    assert Mirror().measure(basis_of(store, tmp_path)).score > 0.9


def test_turning_the_eighth_consolidates(store, tmp_path):
    with store.tick() as t:
        for i in range(5):
            seed_of(t, f"the kettle whistled in the kitchen, time {i}",
                    conditions=("sense:ear",))
    basis = basis_of(store, tmp_path)
    before = Mirror().measure(basis).score
    progress = Mirror().turn(basis)
    assert progress.changed
    assert [s for s in store.all() if s.kind is Kind.DERIVED]
    assert Mirror().measure(basis).score > before


def test_turning_the_eighth_deletes_nothing(store, tmp_path):
    with store.tick() as t:
        members = [seed_of(t, f"the kettle whistled in the kitchen {i}",
                           conditions=("sense:ear",)) for i in range(4)]
    Mirror().turn(basis_of(store, tmp_path))
    assert all(m in store.all() for m in members)


# ── the report ───────────────────────────────────────────────────────

def test_the_turning_renders_every_transformation(store, tmp_path):
    text = measure(basis_of(store, tmp_path)).render()
    for wisdom in ("妙觀察智", "平等性智", "成所作智", "大圓鏡智"):
        assert wisdom in text


def test_the_turning_marks_what_is_not_yet_complete(store, tmp_path):
    """The dashed lines: no transformation is ever reported as finished."""
    with store.tick() as t:
        for i in range(6):
            claim(t, f"someone is there {i}", nature=Nature.PARIKALPITA,
                  pramana=Pramana.APRAMANA)
    text = measure(basis_of(store, tmp_path)).render()
    assert "┄" in text or "incomplete" in text.lower()


def test_an_empty_basis_measures_without_crashing(store, tmp_path):
    result = measure(Basis(store=store))
    assert len(result.progress) == 4
    assert 0.0 <= result.score <= 1.0


def test_the_mirror_stops_counting_redundancy_it_has_already_answered(store, tmp_path):
    """Otherwise the score cannot respond to the turning that addresses it."""
    with store.tick() as t:
        for i in range(5):
            seed_of(t, f"the kettle whistled in the kitchen, time {i}",
                    conditions=("sense:ear",))
    basis = basis_of(store, tmp_path)
    Mirror().turn(basis)
    after = Mirror().measure(basis)
    assert after.score > 0.9
    assert after.metrics["clusters"] == 0


# ── not every provider can be asked to reflect ───────────────────────

def test_a_stub_provider_is_never_asked_to_write_the_self_model(store, tmp_path):
    """The echo provider has no language model behind it. Asking it for a
    corrective and writing the reply into the self-model puts filler where the
    agent's account of itself should be — which is worse than no correction,
    because 恆審思量 carries it into every prompt afterwards."""
    from alaya.providers import EchoProvider

    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I did this myself {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    basis = basis_of(store, tmp_path)
    basis.provider = EchoProvider()
    Equality().turn(basis)
    assert "echo" not in basis.manas.self_model.lower()
    assert "partial" in basis.manas.self_model


def test_a_deliberative_provider_is_asked(store, tmp_path):
    from alaya.providers import Response

    class Model:
        name = "model"
        deliberative = True

        def converse(self, system, messages, tools):
            return Response(text="You have been reading your own attention as character.")

    with store.tick() as t:
        for i in range(8):
            t.perfume(content=f"I did this myself {i}", kind=Kind.ACT,
                      valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                      conditions=("me",))
    basis = basis_of(store, tmp_path)
    basis.provider = Model()
    Equality().turn(basis)
    assert "reading your own attention as character" in basis.manas.self_model
