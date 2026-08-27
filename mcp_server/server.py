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
    alaya_recall      read the store directly, ignoring conditions
    alaya_trace       the full ancestry of a seed
    alaya_manas       the self-model and its bias audit
    alaya_status      the state of the stream
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
)

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
    moment = mano.tick()
    lines = [f"MOMENT {moment.tick}"]
    lines += [f"  arose: [{p.sense.value}] {p.signal}" for p in moment.world.percepts]
    lines += [f"  fired: {s.content} ({s.id[:8]})" for s in moment.world.active]
    for act in moment.acts:
        detail = act.seed.content if act.seed else act.result
        lines.append(f"  did:   {act.tool} — {detail}")
    return "\n".join(lines) if len(lines) > 1 else f"MOMENT {moment.tick} — nothing arose"


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
