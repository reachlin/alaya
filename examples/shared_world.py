"""Two agents, one world, two stores — 共業 in about sixty lines.

Run it:  python examples/shared_world.py

This is the reference agent for the whole architecture, and it exists to
demonstrate one claim precisely: that 唯識 is not solipsism.

Nose has a nose and no ears. Ear has ears and no nose. Neither can perceive what
the other perceives, and there is no world object anywhere in this program. Yet
by the end both hold a congruent picture of a kitchen — because 共相種子 passed
between them and each 變現'd its own.

Watch three things:

  · what does NOT travel. Nose's raw percept is 根身, manifested by karma that
    is Nose's alone. Ear never gets it and never could.
  · what Ear's knowledge is made of. Everything received is 比量 — inferred
    from the fact that somebody said so — and it is tagged that way forever.
  · that the two stores are two files. Nothing is shared but content.
"""
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alaya.common import Commons
from alaya.identity import Identity
from alaya.manas import Manas
from alaya.mano import Mano
from alaya.providers import EchoProvider
from alaya.seeds import Kind, SeedStore
from alaya.senses import DormantFaculty, Sense, SenseField

DIM, BOLD, GOLD, CYAN, RESET = "\033[2m", "\033[1m", "\033[33m", "\033[36m", "\033[0m"

IDENTITY = Identity(
    name="Ālaya",
    purpose="To attend honestly and say only what is borne.",
    hard_rules=("Never claim direct perception for something you inferred.",),
)


def build(root: Path, name: str, faculty: Sense | None):
    """One agent: its own store, its own manas, its own faculties."""
    store = SeedStore(root / f"{name}.jsonl")
    faculties = {s: DormantFaculty(s) for s in Sense}
    return name, store, Mano(
        store=store,
        provider=EchoProvider(),
        senses=SenseField(faculties=faculties),
        manas=Manas(store, path=root / f"{name}-manas.md"),
        identity=IDENTITY,
        speaker=lambda text: print(f"    {BOLD}🗣  {name}: {text}{RESET}"),
    )


def heading(text):
    print(f"\n{BOLD}{text}{RESET}\n{DIM}{'─' * 68}{RESET}")


def main() -> None:
    root = Path(tempfile.mkdtemp(prefix="alaya-shared-"))
    commons = Commons(root / "world.jsonl")

    nose_name, nose_store, nose = build(root, "nose", Sense.NOSE)
    ear_name, ear_store, ear = build(root, "ear", Sense.EAR)

    heading("1 · Nose perceives. Ear is elsewhere and perceives nothing.")
    nose.senses.inject(Sense.NOSE, "bread, baking", extra=("topic:kitchen",))
    nose.tick()
    ear.tick()
    print(f"  {CYAN}nose store{RESET}  {len(nose_store.all())} seeds")
    print(f"  {CYAN}ear store {RESET}  {len(ear_store.all())} seeds — nothing arose for it")

    heading("2 · 共業. Nose offers its 共相種子 to the world.")
    for offering in commons.offer(nose_store, nose_name):
        print(f"  {GOLD}共{RESET} {offering.content}")
    withheld = [s for s in nose_store.all() if s.kind in (Kind.PERCEPT, Kind.REFLECTION)]
    print(f"\n  {DIM}不共 — held back as 根身, manifested by karma that is Nose's alone:{RESET}")
    for seed in withheld:
        print(f"  {DIM}·{RESET} {seed.content}")

    heading("3 · Ear takes it up — as its own seed, not Nose's.")
    for seed in commons.receive(ear_store, ear_name):
        origin = next(c for c in seed.conditions if c.startswith("from:"))
        print(f"  {GOLD}共{RESET} {seed.content}")
        print(f"    {DIM}{seed.kind.value}/{seed.pramana.value} · {origin} · "
              f"id {seed.id[:8]} — Ear's own seed, in Ear's own store{RESET}")

    heading("4 · Now the shared condition fires in Ear's world.")
    with ear_store.tick() as t:
        for seed in t.activate({"topic:kitchen", "from:nose"}):
            print(f"  {GOLD}↑ 種子生現行{RESET} {seed.content}")

    heading("5 · What each agent actually has.")
    for label, store in ((nose_name, nose_store), (ear_name, ear_store)):
        print(f"  {CYAN}{label}{RESET} — {store.path.name}")
        for seed in store.all():
            mark = "現量" if seed.pramana.value == "pratyaksa" else "比量"
            print(f"    {seed.id[:8]} {DIM}{seed.kind.value:<8} {mark}{RESET} {seed.content}")

    print(f"\n{DIM}{'─' * 68}{RESET}")
    print("  Two stores, two files, no shared object anywhere in this program.")
    print("  Ear knows about the bread and never smelled it — and its store says so,")
    print("  permanently, on the face of the seed. 各自變現: each manifests its own.")
    print(f"{DIM}\n  {root}{RESET}")

    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
