"""MCP surface — Ālaya as tools for Claude Code.

ONE SERVER, NOT FIVE — AND WHY
------------------------------
The obvious design is a server per sense: an eye server, an ear server, a nose
server. It is the wrong shape, for three reasons and the third is the real one.

1. **Devices are exclusive.** Two processes cannot both hold the camera. Five
   servers means five processes contending for hardware that admits one owner.

2. **The tick is a transaction.** 三法展轉，因果同時 — activation, action and
   perfuming commit together or not at all. A transaction spanning five stdio
   processes is a distributed transaction, which is a great deal of machinery
   bought in exchange for nothing.

3. **八識不是八個心.** The doctrine is explicit that the eight are functions of
   *one* stream, not eight minds in a committee. Sharding them across processes
   would encode precisely the error the text spends its first chapter refuting.
   Five sense servers would be five little selves — and there are not even eight
   selves here, let alone five.

So: one server, one store, one stream, with a tool per faculty.

    alaya_see / alaya_hear / alaya_smell / alaya_taste / alaya_touch
        place a percept into one sense (現量 — a signal, not a name)
    alaya_moment      live one 刹那 and report what arose and what was done
    alaya_examine     绳蛇检验 — the rope-snake test on a claim
    alaya_recall      read the store directly, ignoring conditions
    alaya_trace       the full ancestry of a seed
    alaya_manas       the self-model and its bias audit
    alaya_status      the state of the stream
    alaya_wisdom      轉識成智 — how far each of the four transformations has come
    alaya_turn        perform one stage of the turning (因中轉 or 果上圓)
"""
from __future__ import annotations

import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from alaya.identity import Identity
from alaya.manas import Manas
from alaya.mano import Mano
from alaya.providers import build
from alaya.seeds import SeedStore
from alaya.senses import DormantFaculty, Ear, Eye, Sense, SenseField
from alaya.directive import Directive
from alaya.trisvabhava import RopeSnake, examine as rope_snake
from alaya.wisdom import Basis, Stage, UntimelyError, measure, turn

ROOT = Path(__file__).resolve().parent.parent

store = SeedStore(os.environ.get("ALAYA_STORE", str(ROOT / "data" / "seeds.jsonl")))
manas = Manas(store, path=Path(store.path).parent / "manas.md")
senses = SenseField(faculties={
    Sense.EYE: DormantFaculty(Sense.EYE) if os.environ.get("ALAYA_NO_EYE") else Eye(),
    Sense.EAR: DormantFaculty(Sense.EAR) if os.environ.get("ALAYA_NO_EAR") else Ear(),
})
mano = Mano(
    store=store,
    provider=build(os.environ.get("ALAYA_PROVIDER", "echo")),
    senses=senses,
    manas=manas,
    identity=Identity.load(os.environ.get("ALAYA_IDENTITY", str(ROOT / "config" / "identity.yaml"))),
    directive=Directive(Path(store.path).parent / "directive.md"),
)


def _basis() -> Basis:
    return Basis(store=store, manas=manas, senses=senses,
                 directive=mano.directive, provider=mano.provider)

if os.environ.get("ALAYA_STRICT"):
    mano.gate = RopeSnake(strict=True)

_last = None  # the most recent moment, so a claim can be examined against it

mcp = MCPServer("alaya", instructions=__doc__)


def _place(sense: Sense, signal: str) -> str:
    senses.inject(sense, signal)
    return f"placed in 前五識/{sense.value}: {signal}"


@mcp.tool()
def alaya_see(signal: str) -> str:
    """眼識 — place a visual percept. Describe the SIGNAL, not the scene."""
    return _place(Sense.EYE, signal)


@mcp.tool()
def alaya_hear(signal: str) -> str:
    """耳識 — place an auditory percept."""
    return _place(Sense.EAR, signal)


@mcp.tool()
def alaya_smell(signal: str) -> str:
    """鼻識 — place an olfactory percept. This faculty has no device."""
    return _place(Sense.NOSE, signal)


@mcp.tool()
def alaya_taste(signal: str) -> str:
    """舌識 — place a gustatory percept. This faculty has no device."""
    return _place(Sense.TONGUE, signal)


@mcp.tool()
def alaya_touch(signal: str) -> str:
    """身識 — place a tactile or proprioceptive percept. No device yet."""
    return _place(Sense.BODY, signal)


@mcp.tool()
def alaya_moment() -> str:
    """Live one 刹那: gather, manifest, deliberate, act, perfume. All or nothing."""
    global _last
    moment = _last = mano.tick()
    lines = [f"MOMENT {moment.tick}"]
    lines += [f"  arose: [{p.sense.value}] {p.signal}" for p in moment.world.percepts]
    lines += [f"  fired: {s.content} ({s.id[:8]})" for s in moment.world.active]
    for act in moment.acts:
        detail = act.seed.content if act.seed else act.result
        lines.append(f"  did:   {act.tool} — {detail}")
    for exam in moment.examinations:
        if exam.fabricated:
            lines.append(f"  遍計所執: {', '.join(exam.fabricated)} (borne by nothing that arose)")
    return "\n".join(lines) if len(lines) > 1 else f"MOMENT {moment.tick} — nothing arose"


@mcp.tool()
def alaya_examine(claim: str) -> str:
    """绳蛇检验 — name what this claim adds that nothing in the last moment bore.

    去掉蛇的是智慧. Reports the 遍計所執 superimposition and what remains sayable
    once it is removed. Records nothing.
    """
    if _last is None:
        return "nothing has arisen yet — call alaya_moment first"
    grounds = [*_last.world.active, *_last.percept_seeds]
    return rope_snake(claim, grounds).render()


@mcp.tool()
def alaya_recall(query: str = "", n: int = 10) -> str:
    """Read the store directly, ignoring 待眾緣. Reading is not arising."""
    found = store.recall(query or None, n=n)
    return "\n".join(
        f"{s.id[:8]} [{s.kind.value}/{s.pramana.value}] {s.content}" for s in found
    ) or "nothing found"


@mcp.tool()
def alaya_trace(seed_id: str) -> str:
    """引自果's record — walk a seed's full ancestry back to the percepts."""
    match = next((s for s in store.all() if s.id.startswith(seed_id)), None)
    if match is None:
        return "no such seed"
    return "\n".join(
        f"{'  ' * min(i, 6)}{s.id[:8]} [{s.kind.value}/{s.pramana.value} t{s.tick}] {s.content}"
        for i, s in enumerate(store.trace(match.id))
    )


@mcp.tool()
def alaya_manas() -> str:
    """第七末那識 — the self-model, and how much it has been bending conduct."""
    return f"{manas.color()}\n\n── audit ──\n{manas.audit().render()}"


@mcp.tool()
def alaya_wisdom() -> str:
    """轉識成智 — how far each of the four transformations has come. Changes nothing."""
    return measure(_basis()).render()


@mcp.tool()
def alaya_turn(stage: str = "cause") -> str:
    """Perform one stage of 轉依.

    stage="cause" (因中轉) turns the 6th and 7th — cheap, safe while running.
    stage="fruit" (果上圓) turns the 5th and 8th — needs a settled store, so it
    refuses if a moment is open.
    """
    wanted = Stage.FRUIT if stage.lower().startswith("f") else Stage.CAUSE
    try:
        return turn(_basis(), stage=wanted).render()
    except UntimelyError as exc:
        return f"untimely: {exc}"


@mcp.tool()
def alaya_status() -> str:
    """The state of the stream."""
    seeds = store.all()
    feeds = " · ".join(
        f"{s.value}{'✓' if live else '—'}" for s, live in senses.available().items()
    )
    return (f"tick {store.tick_count} · {len(seeds)} seeds · "
            f"{len({s.lineage for s in seeds})} lineages\nsenses: {feeds}\n"
            f"provider: {mano.provider.name}\nstore: {store.path}")


if __name__ == "__main__":
    mcp.run()
