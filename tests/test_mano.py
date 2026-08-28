"""第六意識 — the layer that names, decides, and acts.

意識 is 遍緣一切法 (it can take anything as object) and 造業最強 (it makes the
most karma). It is also 通三量: it can be direct, inferred, or mistaken. This
file pins down the one design decision that follows from that — the measure of
a claim is *computed from what actually arose*, never asserted by the model.
"""
import pytest

from alaya.identity import Identity
from alaya.mano import Mano
from alaya.manas import Manas
from alaya.providers import Call, EchoProvider, Response
from alaya.seeds import Kind, Pramana, Valence
from alaya.senses import DormantFaculty, Sense, SenseField, Source


def build(store, tmp_path, script=None, speaker=None):
    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    return Mano(
        store=store,
        provider=EchoProvider(script=script),
        senses=field,
        manas=Manas(store, path=tmp_path / "manas.md"),
        identity=Identity(name="Ālaya", purpose="to witness", hard_rules=("be honest",)),
        speaker=speaker,
    ), field


def call(name, **args):
    return Call(name=name, args=args, id=f"c-{name}")


# ── the moment ───────────────────────────────────────────────────────

def test_a_tick_with_nothing_happening_still_happens(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[]])
    moment = mano.tick()
    assert moment.tick == 1
    assert moment.acts == ()


def test_percepts_become_seeds_of_direct_perception(store, tmp_path):
    mano, field = build(store, tmp_path, script=[[]])
    field.inject(Sense.NOSE, "pizza, cooling")
    moment = mano.tick()
    (seed,) = moment.percept_seeds
    assert seed.kind is Kind.PERCEPT
    assert seed.pramana is Pramana.PRATYAKSA
    assert seed.content == "pizza, cooling"


def test_a_transcript_is_recorded_as_inference_not_perception(store, tmp_path):
    """Hearing sound is 現量. Hearing *words* is already 分別 — 比量 at best."""
    mano, field = build(store, tmp_path, script=[[]])
    field.inject(Sense.EAR, "is the kettle on", extra=("form:speech",))
    moment = mano.tick()
    (seed,) = moment.percept_seeds
    assert seed.kind is Kind.CLAIM
    assert seed.pramana is Pramana.ANUMANA


def test_percept_conditions_are_carried_onto_the_seed(store, tmp_path):
    mano, field = build(store, tmp_path, script=[[]])
    field.inject(Sense.NOSE, "pizza")
    (seed,) = mano.tick().percept_seeds
    assert "sense:nose" in seed.conditions
    assert "source:injected" in seed.conditions


# ── 造業 — acting ────────────────────────────────────────────────────

def test_speaking_lays_down_an_act_seed(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[call("speak", text="I am here")], []])
    moment = mano.tick()
    assert moment.spoken == ("I am here",)
    (act,) = [s for s in store.all() if s.kind is Kind.ACT]
    assert act.content == "I am here"


def test_the_speaker_is_invoked(store, tmp_path):
    said = []
    mano, _ = build(store, tmp_path, script=[[call("speak", text="hello")], []],
                    speaker=said.append)
    mano.tick()
    assert said == ["hello"]


def test_an_act_is_traceable_to_what_gave_rise_to_it(store, tmp_path):
    """引自果 is not this — but 果俱有's record makes the walk total."""
    mano, field = build(store, tmp_path, script=[[call("speak", text="something smells good")], []])
    field.inject(Sense.NOSE, "pizza, cooling")
    mano.tick()
    (act,) = [s for s in store.all() if s.kind is Kind.ACT]
    assert any("pizza" in s.content for s in store.trace(act.id))


# ── 三量 — the measure is computed, never claimed ────────────────────

def test_a_claim_with_something_behind_it_is_inference(store, tmp_path):
    mano, field = build(store, tmp_path, script=[[call("remember", content="someone is cooking")], []])
    field.inject(Sense.NOSE, "pizza, cooling")
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.pramana is Pramana.ANUMANA


def test_a_claim_with_nothing_behind_it_is_erroneous(store, tmp_path):
    """非量 — discrimination the object does not bear. Nothing arose to bear it."""
    mano, _ = build(store, tmp_path, script=[[call("remember", content="someone is cooking")], []])
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.pramana is Pramana.APRAMANA


def test_the_model_cannot_upgrade_its_own_measure(store, tmp_path):
    """A model asserting its claim is direct does not make it direct."""
    mano, _ = build(
        store, tmp_path,
        script=[[call("remember", content="a snake", measure="direct")], []],
    )
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.pramana is not Pramana.PRATYAKSA


def test_the_model_may_downgrade_its_own_measure(store, tmp_path):
    """Doubt is always available, even when the grounding is there."""
    mano, field = build(
        store, tmp_path,
        script=[[call("remember", content="someone is cooking", measure="uncertain")], []],
    )
    field.inject(Sense.NOSE, "pizza")
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.pramana is Pramana.APRAMANA


def test_no_claim_the_sixth_consciousness_makes_is_ever_direct(store, tmp_path):
    """現量 belongs to the senses. Naming is not perceiving, however sure it feels."""
    mano, field = build(store, tmp_path, script=[[call("remember", content="a dog")], []])
    field.inject(Sense.EAR, "0.5s audio · rms 0.9 · peak 1.0")
    mano.tick()
    claims = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert all(c.pramana is not Pramana.PRATYAKSA for c in claims)


# ── the other tools ──────────────────────────────────────────────────

def test_recall_reads_without_writing(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[call("recall", query="kettle")], []])
    before = len(store.all())
    moment = mano.tick()
    assert not [s for s in store.all() if s.kind is Kind.ACT]
    assert moment.acts[0].tool == "recall"


def test_attend_widens_what_can_arise(store, tmp_path):
    """作意 — volition supplying a missing condition so a seed can fire."""
    from tests.conftest import percept as seed_of
    with store.tick() as t:
        seed_of(t, "she said she'd call at six", conditions=("topic:call",))

    mano, _ = build(store, tmp_path, script=[[call("attend", conditions=["topic:call"])], []])
    moment = mano.tick()
    assert "she said she'd call at six" in moment.acts[0].result


def test_feeling_lays_down_a_reflection(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[call("feel", mood="uneasy")], []])
    mano.tick()
    (r,) = [s for s in store.all() if s.kind is Kind.REFLECTION]
    assert "uneasy" in r.content


# ── robustness ───────────────────────────────────────────────────────

def test_an_unknown_tool_is_reported_not_fatal(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[call("fly")], []])
    moment = mano.tick()
    assert "unknown" in moment.acts[0].result.lower()


def test_a_failing_tool_does_not_abort_the_moment(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[call("speak"), call("feel", mood="ok")], []])
    moment = mano.tick()
    assert len(moment.acts) == 2


def test_a_provider_failure_rolls_the_whole_moment_back(store, tmp_path):
    """三法展轉 — the moment commits together or not at all."""
    class Broken(EchoProvider):
        def converse(self, system, messages, tools):
            raise RuntimeError("no model")

    mano, field = build(store, tmp_path, script=[[]])
    mano.provider = Broken()
    field.inject(Sense.NOSE, "pizza")
    with pytest.raises(RuntimeError):
        mano.tick()
    assert store.all() == ()


def test_the_rounds_are_bounded(store, tmp_path):
    class Loops(EchoProvider):
        def converse(self, system, messages, tools):
            return Response(text=None, calls=[call("feel", mood="again")])

    mano, _ = build(store, tmp_path)
    mano.provider = Loops()
    mano.max_rounds = 3
    moment = mano.tick()
    assert len(moment.acts) == 3


# ── 恆審思量 — manas is always in the prompt ─────────────────────────

def test_the_self_model_reaches_the_provider(store, tmp_path):
    seen = {}

    class Watching(EchoProvider):
        def converse(self, system, messages, tools):
            seen["system"] = system
            seen["user"] = messages[0]["content"]
            return Response(text="ok", calls=[])

    mano, _ = build(store, tmp_path)
    mano.manas.revise("I am the one who waits by the door.")
    mano.provider = Watching()
    mano.tick()
    assert "waits by the door" in seen["user"]
    assert "Ālaya" in seen["system"]
    assert "be honest" in seen["system"]


# ── 三性 in the action path — the rope-snake gate ────────────────────

def test_a_claim_that_only_restates_what_arose_is_dependent(store, tmp_path):
    from alaya.seeds import Nature
    mano, field = build(store, tmp_path, script=[[call("remember", content="pizza cooling")], []])
    field.inject(Sense.NOSE, "pizza, cooling")
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.nature is Nature.PARATANTRA


def test_a_claim_that_exceeds_what_arose_is_recorded_as_fabricated(store, tmp_path):
    """情有理無 — the excess is real to the agent and grounded in nothing."""
    from alaya.seeds import Nature
    mano, field = build(
        store, tmp_path,
        script=[[call("remember", content="pizza left by my neighbour")], []],
    )
    field.inject(Sense.NOSE, "pizza, cooling")
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.nature is Nature.PARIKALPITA


def test_the_measure_is_not_demoted_by_a_literal_examiner(store, tmp_path):
    """A crude lexical test must not be able to call a real inference 非量.
    三量 stays on provenance; 三性 is what the gate governs."""
    mano, field = build(
        store, tmp_path,
        script=[[call("remember", content="someone is cooking")], []],
    )
    field.inject(Sense.NOSE, "pizza, cooling")
    mano.tick()
    (claim,) = [s for s in store.all() if s.kind is Kind.CLAIM]
    assert claim.pramana is Pramana.ANUMANA


def test_the_examination_is_reported_back_to_the_model(store, tmp_path):
    mano, field = build(
        store, tmp_path,
        script=[[call("remember", content="pizza left by my neighbour")], []],
    )
    field.inject(Sense.NOSE, "pizza, cooling")
    moment = mano.tick()
    assert "neighbour" in moment.acts[0].result


def test_the_moment_carries_its_examinations(store, tmp_path):
    mano, field = build(store, tmp_path, script=[[call("remember", content="a snake")], []])
    field.inject(Sense.EYE, "a coiled shape")
    moment = mano.tick()
    assert len(moment.examinations) == 1
    assert moment.examinations[0].claim == "a snake"


def test_the_model_can_examine_a_claim_before_committing_to_it(store, tmp_path):
    """智慧 — the gate is available to the sixth consciousness, not only over it."""
    mano, field = build(store, tmp_path, script=[[call("examine", claim="a snake")], []])
    field.inject(Sense.EYE, "a coiled shape on the path")
    moment = mano.tick()
    assert "unfounded" in moment.acts[0].result.lower()
    assert not [s for s in store.all() if s.kind is Kind.CLAIM]


# ── strict mode ──────────────────────────────────────────────────────

def test_by_default_an_unfounded_act_is_marked_not_blocked(store, tmp_path):
    """無覆無記 — the default is to name the superimposition, not to censor it."""
    mano, _ = build(store, tmp_path, script=[[call("speak", text="someone is at the door")], []])
    moment = mano.tick()
    assert moment.spoken == ("someone is at the door",)


def test_strict_mode_refuses_an_unfounded_outward_act(store, tmp_path):
    from alaya.trisvabhava import RopeSnake
    mano, _ = build(store, tmp_path, script=[[call("speak", text="someone is at the door")], []])
    mano.gate = RopeSnake(strict=True)
    moment = mano.tick()
    assert moment.spoken == ()
    assert "refused" in moment.acts[0].result.lower()
    assert not [s for s in store.all() if s.kind is Kind.ACT]


def test_strict_mode_tells_the_model_what_it_may_say_instead(store, tmp_path):
    """去掉蛇的是智慧 — and then say what the rope actually is."""
    from alaya.trisvabhava import RopeSnake
    mano, field = build(
        store, tmp_path,
        script=[[call("speak", text="my neighbour is here")], []],
    )
    mano.gate = RopeSnake(strict=True)
    field.inject(Sense.NOSE, "pizza, cooling")
    moment = mano.tick()
    assert "pizza" in moment.acts[0].result


def test_strict_mode_allows_a_grounded_act(store, tmp_path):
    from alaya.trisvabhava import RopeSnake
    mano, field = build(store, tmp_path, script=[[call("speak", text="pizza, cooling")], []])
    mano.gate = RopeSnake(strict=True)
    field.inject(Sense.NOSE, "pizza, cooling")
    assert mano.tick().spoken == ("pizza, cooling",)


# ── 妙觀察智's directive reaches the layer it was written for ────────

def test_the_directive_reaches_the_prompt(store, tmp_path):
    """因中轉 closes the loop only if the sixth consciousness actually reads it."""
    from alaya.directive import Directive
    seen = {}

    class Watching(EchoProvider):
        def converse(self, system, messages, tools):
            seen["user"] = messages[0]["content"]
            return Response(text="ok", calls=[])

    directive = Directive(tmp_path / "directive.md")
    directive.write("Call examine() before you remember anything.")
    mano, _ = build(store, tmp_path)
    mano.directive = directive
    mano.provider = Watching()
    mano.tick()
    assert "Call examine() before you remember anything." in seen["user"]


def test_an_agent_with_no_directive_still_lives(store, tmp_path):
    mano, _ = build(store, tmp_path, script=[[]])
    assert mano.directive is None
    assert mano.tick().tick == 1
