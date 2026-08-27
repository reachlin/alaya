"""第六意識 — the layer that names, decides, and acts.

WHAT THE DOCTRINE SAYS ABOUT IT
--------------------------------
Three phrases characterise the sixth consciousness, and each one turns into a
design decision in this file.

**遍緣一切法** — it takes anything whatever as its object. Unlike the five
senses, each locked to its own kind of object, 意識 ranges over everything
including the past, the absent, and the merely possible. In code: it is the
only layer given the whole world plus the store plus its own self-model.

**造業最強** — it is the strongest maker of karma. The senses receive; manas
broods; the store keeps. Only the sixth *does* things. So this is the only
module that executes tools, and every execution lays down a seed. There is no
side door: an act that left no seed would be an act outside causation.

**通三量** — it is permeable to all three measures of knowledge. It can be
direct (現量), inferential (比量), or plain wrong (非量). And this is where the
design gets interesting.

THE ONE IMPORTANT DECISION IN THIS FILE
----------------------------------------
An agent cannot be trusted to rate its own certainty. Ask a model whether its
claim is grounded and it will say yes, because fluency and confidence are the
same signal in a language model. So **the measure is computed, never asserted**:

    something arose this moment that the claim rests on   →  比量 ANUMANA
    nothing arose; the claim is free-floating             →  非量 APRAMANA

The model is given a ``measure`` argument, but it can only ever *downgrade* —
express doubt — never upgrade. And 現量 is not on the menu at all: 前五識唯現量,
direct perception belongs to the senses, and no amount of confidence turns a
名言 into an observation. That single asymmetry is a real hallucination control,
and the doctrine handed us the vocabulary for it fully formed.

The rope and the snake are the classical illustration, and note which axis they
sit on: mistaking a rope for a snake is 非量 — a *cognition* that the object
does not bear — while the rope's own status as 依他起 (dependently arisen, not
independently real) is 三性, a different question entirely. Phase 1 conflated
these. Seeds now carry both.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from alaya.identity import Identity
from alaya.manas import Manas
from alaya.manifest import World, manifest
from alaya.providers import Call, Provider, ToolSpec
from alaya.seeds import Kind, Nature, Pramana, Seed, SeedStore, Tick, Valence
from alaya.senses import Percept, SenseField
from alaya.trisvabhava import Examination, RopeSnake, Verdict

# ── 造業 — the act surface ───────────────────────────────────────────

TOOLS = [
    ToolSpec(
        name="speak",
        description="Say something aloud. This is an outward act and is recorded as one.",
        schema={"type": "object", "properties": {"text": {"type": "string"}},
                "required": ["text"]},
    ),
    ToolSpec(
        name="remember",
        description=(
            "Lay down a claim about what is going on. The measure of knowledge is "
            "computed from what actually arose this moment — you may pass "
            "measure='uncertain' to mark a claim as doubtful, but you cannot mark one "
            "as certain. Direct perception is not available to you: naming is not "
            "perceiving."
        ),
        schema={"type": "object", "properties": {
            "content": {"type": "string"},
            "measure": {"type": "string", "enum": ["inferred", "uncertain"]},
            "valence": {"type": "string", "enum": ["wholesome", "unwholesome", "neutral"]},
        }, "required": ["content"]},
    ),
    ToolSpec(
        name="recall",
        description="Read the store directly, ignoring conditions. Reading is not acting.",
        schema={"type": "object", "properties": {"query": {"type": "string"}}},
    ),
    ToolSpec(
        name="attend",
        description=(
            "作意 — supply a condition on purpose so that seeds needing it can arise. "
            "Use when you suspect you know something that has not come to mind."
        ),
        schema={"type": "object", "properties": {
            "conditions": {"type": "array", "items": {"type": "string"}}},
            "required": ["conditions"]},
    ),
    ToolSpec(
        name="examine",
        description=(
            "绳蛇检验 — run the rope-snake test on a claim before you commit to it. "
            "Names what the claim adds that nothing arising this moment bears, and "
            "tells you what remains sayable once that is removed. Costs nothing and "
            "records nothing."
        ),
        schema={"type": "object", "properties": {"claim": {"type": "string"}},
                "required": ["claim"]},
    ),
    ToolSpec(
        name="feel",
        description="Record how this moment sits with you. A reflection, not an outward act.",
        schema={"type": "object", "properties": {"mood": {"type": "string"}},
                "required": ["mood"]},
    ),
]

TOOL_NAMES = tuple(t.name for t in TOOLS)


@dataclass(frozen=True)
class Act:
    tool: str
    args: dict
    result: str
    seed: Seed | None = None


@dataclass(frozen=True)
class Moment:
    """One complete turning of the stream — what arose, and what was done."""

    tick: int
    world: World
    percept_seeds: tuple[Seed, ...] = ()
    acts: tuple[Act, ...] = ()
    spoken: tuple[str, ...] = ()
    examinations: tuple[Examination, ...] = ()
    text: str | None = None


class Mano:
    def __init__(
        self,
        store: SeedStore,
        provider: Provider,
        senses: SenseField,
        manas: Manas,
        identity: Identity,
        speaker: Callable[[str], None] | None = None,
        gate: RopeSnake | None = None,
        max_rounds: int = 4,
    ):
        self.store = store
        self.provider = provider
        self.senses = senses
        self.manas = manas
        self.identity = identity
        self.speaker = speaker
        # 绳蛇检验 in the action path. Default marks rather than blocks — see
        # RopeSnake's docstring for why 無覆無記 is carried up this far.
        self.gate = gate or RopeSnake()
        self.max_rounds = max_rounds

    # ── one moment ───────────────────────────────────────────────────

    def tick(self, attend: Iterable[str] = ()) -> Moment:
        """Live one moment: gather, manifest, deliberate, act, perfume.

        All of it inside a single :class:`~alaya.seeds.Tick`, because 三法展轉
        因果同時 — seed, manifestation and newly-perfumed seed are one
        transaction. If the model fails halfway, the moment did not happen: the
        percepts roll back with everything else rather than leaving the store
        holding half a cause.
        """
        percepts = self.senses.gather()

        with self.store.tick() as t:
            world = manifest(
                t, percepts, self.senses.available(), TOOL_NAMES, extra_conditions=attend
            )
            percept_seeds = tuple(self._seed_for(t, p) for p in percepts)

            # 果俱有 — everything an act may cite has to be present *now*. These
            # are exactly the seeds that arose or were laid down this moment.
            grounds: list[Seed] = [*world.active, *percept_seeds]

            acts: list[Act] = []
            spoken: list[str] = []
            examinations: list[Examination] = []
            final_text: str | None = None

            messages = [{"role": "user", "content": self._user_prompt(world)}]
            system = self._system_prompt()

            for _ in range(self.max_rounds):
                response = self.provider.converse(system, messages, TOOLS)
                if not response.calls:
                    final_text = response.text
                    break
                messages.append({"role": "assistant", "content": response.text or "",
                                 "calls": [c.name for c in response.calls]})
                for c in response.calls:
                    act = self._execute(t, c, grounds, examinations)
                    acts.append(act)
                    if act.tool == "speak" and act.seed is not None:
                        spoken.append(act.seed.content)
                    messages.append({"role": "tool", "tool_call_id": c.id,
                                     "content": act.result})

        return Moment(
            tick=world.tick,
            world=world,
            percept_seeds=percept_seeds,
            acts=tuple(acts),
            spoken=tuple(spoken),
            examinations=tuple(examinations),
            text=final_text,
        )

    # ── 現量 into the store ──────────────────────────────────────────

    def _seed_for(self, t: Tick, p: Percept) -> Seed:
        """Turn one percept into one seed, at the correct measure of knowledge.

        This is where :mod:`alaya.senses.ear` hands off its unfinished business.
        A transcript arrives tagged ``form:speech``, and a transcript is not
        sound — it is a speech model's *discrimination* of sound, fallible in
        exactly the way 現量 cannot be. So it is recorded as a CLAIM reached by
        比量, while everything else the senses deliver is a PERCEPT by 現量.
        """
        if "form:speech" in p.conditions:
            return t.perfume(
                content=p.signal,
                kind=Kind.CLAIM,
                valence=Valence.NEUTRAL,
                nature=Nature.PARATANTRA,
                pramana=Pramana.ANUMANA,
                conditions=p.conditions,
            )
        return t.perfume(
            content=p.signal,
            kind=Kind.PERCEPT,
            valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA,
            pramana=Pramana.PRATYAKSA,   # 前五識唯現量, enforced again in Seed.arise
            conditions=p.conditions,
        )

    # ── 造業 — executing what the model decided ──────────────────────

    def _execute(self, t: Tick, call: Call, grounds: list[Seed],
                 examinations: list[Examination]) -> Act:
        try:
            return self._dispatch(t, call, grounds, examinations)
        except Exception as exc:
            # A failed act is still something that happened. It is reported back
            # to the model in the same moment so it can respond to its own
            # failure rather than repeating it.
            return Act(tool=call.name, args=call.args, result=f"failed: {exc}")

    def _dispatch(self, t: Tick, call: Call, grounds: list[Seed],
                  examinations: list[Examination]) -> Act:
        args = call.args or {}
        parents = [s.id for s in grounds]

        if call.name == "speak":
            text = args["text"]
            # 绳蛇检验 before an outward act — the one place in the system where
            # something may be refused, and only when the gate is strict.
            exam = self.gate.examine(text, grounds)
            examinations.append(exam)
            if not self.gate.permits(exam):
                return Act(call.name, args,
                           f"refused — this act rests on nothing that arose.\n{exam.render()}")
            if self.speaker:
                self.speaker(text)
            seed = t.perfume(content=text, kind=Kind.ACT, valence=Valence.NEUTRAL,
                             nature=exam.nature, parents=parents)
            return Act(call.name, args, "said", seed)

        if call.name == "remember":
            exam = self.gate.examine(args["content"], grounds)
            examinations.append(exam)
            seed = t.perfume(
                content=args["content"],
                kind=Kind.CLAIM,
                valence=Valence(args.get("valence", "neutral")),
                # 三性 from the examination — does the claim exceed its basis?
                nature=exam.nature,
                # 三量 from provenance — did anything arise to reason from? These
                # are different questions and a literal examiner must not be able
                # to answer the second one.
                pramana=self._measure(args.get("measure"), grounds),
                parents=parents,
            )
            return Act(call.name, args,
                       f"remembered as {seed.pramana.value}/{seed.nature.value}\n{exam.render()}",
                       seed)

        if call.name == "examine":
            exam = self.gate.examine(args["claim"], grounds)
            examinations.append(exam)
            return Act(call.name, args, exam.render())

        if call.name == "recall":
            found = self.store.recall(args.get("query"), n=int(args.get("n", 5)))
            body = "\n".join(f"· {s.content}" for s in found) or "nothing found"
            return Act(call.name, args, body)

        if call.name == "attend":
            arisen = t.activate(set(args["conditions"]))
            grounds.extend(s for s in arisen if s not in grounds)
            body = "\n".join(f"· {s.content}" for s in arisen) or "nothing arose"
            return Act(call.name, args, body)

        if call.name == "feel":
            seed = t.perfume(content=f"felt {args['mood']}", kind=Kind.REFLECTION,
                             valence=Valence.NEUTRAL, nature=Nature.PARATANTRA,
                             parents=parents)
            return Act(call.name, args, "noted", seed)

        return Act(call.name, args, f"unknown tool: {call.name}")

    @staticmethod
    def _measure(declared: str | None, grounds: list[Seed]) -> Pramana:
        """三量, decided by the moment rather than by the model's confidence.

        Downgrades are honoured; upgrades are not; 現量 is never reachable. A
        model that says "measure=direct" is told nothing and gets 比量 or 非量
        exactly as if it had said nothing, because the question of whether a
        claim is borne out is not one the claimant gets to settle.
        """
        if not grounds:
            return Pramana.APRAMANA       # 非量 — nothing arose to bear this
        if declared == "uncertain":
            return Pramana.APRAMANA       # doubt is always available
        return Pramana.ANUMANA            # 比量 — reached through what arose

    # ── prompts ──────────────────────────────────────────────────────

    def _system_prompt(self) -> str:
        rules = "\n".join(f"- {r}" for r in self.identity.hard_rules)
        tools = "\n".join(f"- {t.name}: {t.description}" for t in TOOLS)
        return f"""You are {self.identity.name}, the sixth consciousness of a mind built on the
Yogācāra model. You are the only layer of this mind that can act.

PURPOSE
{self.identity.purpose}

HARD RULES (no layer may rewrite these)
{rules}

WHAT YOU ARE WORKING WITH
The five senses deliver signals, never names. "luminance 0.42" is what the eye
gives you; "a lit room" is something *you* would be adding. That addition is
legitimate and necessary — it is your function — but it is recorded as your
inference, not as observation.

The store shows you seeds whose conditions the present moment happened to meet.
What has not arisen is not absent from the world; it merely did not fire. Use
attend() when you suspect you know something that has not come to mind.

YOUR TOOLS
{tools}

Speak in {self.identity.language}."""

    def _user_prompt(self, world: World) -> str:
        # 恆審思量 — manas is in every prompt. No agent gets to skip its priors;
        # the most it can do is be shown them.
        return f"{world.render()}\n\n{self.manas.color(world)}\n\nWhat do you do?"
