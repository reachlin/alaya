"""The console — where a human meets the stream.

The parsing rule is one line long: **what you type reaches the agent the way it
would reach a mind.** If you address a sense ("you smell pizza"), it arrives at
that sense as a percept. If you address the agent ("are you there"), it arrives
through the ear as speech — because that is how speech gets into a mind, and
because it means the agent has to *hear* you rather than being handed a
privileged channel no perception passes through.

Injected percepts are marked ``source:injected`` and stay marked forever. The
agent cannot tell the difference from the inside — nothing can, that is what it
means for a percept to arise — but anyone reading ``trace()`` afterwards can
see precisely which of its conclusions rest on things a human typed.

WHY THE HUMAN DRIVES THE TICK
-----------------------------
By default nothing happens until you press Enter. The stream in the doctrine is
恆轉如瀑流, ceaseless — and ``/auto`` will give you that — but a mind you can
step through one 刹那 at a time is a mind you can actually inspect, and this
console is for looking at the machinery.
"""
from __future__ import annotations

import re
import shlex
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from alaya.manas import Manas
from alaya.mano import Mano, Moment
from alaya.seeds import Kind, SeedStore
from alaya.senses import Sense, SenseField, Source

# ── what a line of input turns into ──────────────────────────────────


@dataclass(frozen=True)
class Advance:
    count: int = 1


@dataclass(frozen=True)
class Inject:
    sense: Sense
    signal: str


@dataclass(frozen=True)
class Speech:
    text: str


@dataclass(frozen=True)
class Command:
    name: str
    args: tuple[str, ...] = ()


@dataclass(frozen=True)
class Quit:
    pass


#: The verb each sense answers to. Past and third-person forms are accepted
#: because people type "you smelled smoke" as readily as "you smell smoke".
VERBS = {
    Sense.EYE: ("see", "sees", "saw", "seen"),
    Sense.EAR: ("hear", "hears", "heard"),
    Sense.NOSE: ("smell", "smells", "smelled", "smelt"),
    Sense.TONGUE: ("taste", "tastes", "tasted"),
    Sense.BODY: ("feel", "feels", "felt", "touch", "touched"),
}
_VERB_TO_SENSE = {verb: sense for sense, verbs in VERBS.items() for verb in verbs}
_ALL_VERBS = "|".join(sorted(_VERB_TO_SENSE, key=len, reverse=True))

#: "you hear a dog bark" — the second person, because you are telling the agent
#: what *it* perceives, not reporting your own experience.
_SECOND_PERSON = re.compile(rf"^\s*(?:you|u)\s+({_ALL_VERBS})\s+(.+)$", re.IGNORECASE)
_SLASH_SENSE = re.compile(rf"^/({_ALL_VERBS})\s+(.+)$", re.IGNORECASE)

QUIT_WORDS = {"quit", "exit", "q"}


def parse(line: str):
    """Turn one line of input into an intention. Pure — this is the tested part."""
    text = line.strip()
    if not text:
        return Advance(1)

    match = _SLASH_SENSE.match(text) or _SECOND_PERSON.match(text)
    if match:
        return Inject(_VERB_TO_SENSE[match.group(1).lower()], match.group(2).strip())

    if text.startswith("/"):
        try:
            parts = shlex.split(text[1:])
        except ValueError:
            parts = text[1:].split()
        if not parts:
            return Advance(1)
        name, args = parts[0].lower(), tuple(parts[1:])
        if name in QUIT_WORDS:
            return Quit()
        if name == "tick":
            count = int(args[0]) if args and args[0].isdigit() else 1
            return Advance(count)
        return Command(name, args)

    return Speech(text)


# ── the loop ─────────────────────────────────────────────────────────

DIM, BOLD, RESET = "\033[2m", "\033[1m", "\033[0m"
CYAN, GOLD, RED = "\033[36m", "\033[33m", "\033[31m"

HELP = """
  <enter>              live one moment
  /tick N              live N moments
  you smell pizza      place a percept in a sense (see/hear/smell/taste/feel)
  /smell pizza         the same, in short form
  anything else        spoken aloud — the agent hears it through its ear

  /status              the stream: tick, seeds, lineages
  /senses              which faculties have a feed
  /world               what would arise right now, without acting
  /recall <query>      read the store directly (ignores conditions)
  /trace <id>          the full ancestry of a seed — 果俱有's record
  /manas               the self-model, and what it was built from
  /audit               how that self-model has been skewing conduct
  /auto [secs]         let the stream run on its own    /stop to halt it
  /help  /quit
"""


class Console:
    def __init__(self, mano: Mano, store: SeedStore, manas: Manas, senses: SenseField):
        self.mano = mano
        self.store = store
        self.manas = manas
        self.senses = senses
        self._auto: threading.Thread | None = None
        self._stop = threading.Event()

    # ── rendering one moment ─────────────────────────────────────────

    def show(self, moment: Moment) -> None:
        print(f"\n{DIM}── 刹那 {moment.tick} ─────────────────────────{RESET}")
        for p in moment.world.percepts:
            tag = f"{p.sense.value}·injected" if p.source is Source.INJECTED else p.sense.value
            print(f"  {CYAN}◦ [{tag}]{RESET} {p.signal}")
        for s in moment.world.active:
            print(f"  {GOLD}↑ 種子生現行{RESET} {s.content} {DIM}({s.id[:8]}){RESET}")
        for act in moment.acts:
            mark = f"{BOLD}{act.tool}{RESET}"
            detail = act.seed.content if act.seed else act.result.replace("\n", " / ")
            # 三量 describes a cognition, so it is shown for claims and percepts.
            # An act is not a cognition; printing a measure on it would suggest
            # the doing was more or less well-founded, which is a category error.
            shows_measure = act.seed is not None and act.seed.kind in (Kind.CLAIM, Kind.DERIVED)
            measure = f" {DIM}[{act.seed.pramana.value}]{RESET}" if shows_measure else ""
            print(f"  → {mark} {detail}{measure}")
        if moment.text:
            print(f"  {DIM}{moment.text}{RESET}")
        if not (moment.world.percepts or moment.world.active or moment.acts):
            print(f"  {DIM}(nothing arose){RESET}")

    # ── commands ─────────────────────────────────────────────────────

    def command(self, name: str, args: tuple[str, ...]) -> None:
        if name == "help":
            print(HELP)
        elif name == "status":
            seeds = self.store.all()
            lineages = {s.lineage for s in seeds}
            print(f"  tick {self.store.tick_count} · {len(seeds)} seeds · "
                  f"{len(lineages)} lineages · store {self.store.path}")
        elif name == "senses":
            for sense, live in self.senses.available().items():
                print(f"  {sense.value:<7} {'open' if live else '—  (injection only)'}")
        elif name == "world":
            with self.store.tick() as t:
                from alaya.manifest import manifest
                from alaya.mano import TOOL_NAMES
                world = manifest(t, [], self.senses.available(), TOOL_NAMES)
                print(world.render())
                raise _Rollback  # looking is not living; do not commit a moment
        elif name == "recall":
            found = self.store.recall(" ".join(args) or None, n=10)
            for s in found:
                print(f"  {s.id[:8]} {DIM}{s.kind.value}/{s.pramana.value}{RESET} {s.content}")
            if not found:
                print("  nothing found")
        elif name == "trace":
            if not args:
                print("  usage: /trace <seed id or prefix>")
                return
            match = next((s for s in self.store.all() if s.id.startswith(args[0])), None)
            if match is None:
                print("  no such seed")
                return
            for depth, s in enumerate(self.store.trace(match.id)):
                print(f"  {'  ' * min(depth, 6)}{s.id[:8]} {DIM}{s.kind.value}/"
                      f"{s.pramana.value} t{s.tick}{RESET} {s.content}")
        elif name == "manas":
            print(self.manas.color())
        elif name == "audit":
            print(self.manas.audit().render())
        elif name == "auto":
            self.start_auto(float(args[0]) if args else 5.0)
        elif name == "stop":
            self.stop_auto()
        else:
            print(f"  unknown command /{name} — try /help")

    # ── 恆轉如瀑流 — letting it run ──────────────────────────────────

    def start_auto(self, seconds: float) -> None:
        if self._auto and self._auto.is_alive():
            print("  already running")
            return
        self._stop.clear()

        def run():
            while not self._stop.wait(seconds):
                try:
                    self.show(self.mano.tick())
                except Exception as exc:
                    print(f"  {RED}moment failed:{RESET} {exc}")

        self._auto = threading.Thread(target=run, daemon=True)
        self._auto.start()
        print(f"  stream running every {seconds:g}s — /stop to halt")

    def stop_auto(self) -> None:
        self._stop.set()
        if self._auto:
            self._auto.join(timeout=2)
        print("  stream halted")

    # ── the REPL ─────────────────────────────────────────────────────

    def run(self) -> None:
        print(f"{BOLD}Ālaya · 阿賴耶{RESET} — eight consciousnesses, one stream")
        print(f"{DIM}provider: {self.mano.provider.name} · store: {self.store.path} · "
              f"/help for commands{RESET}")
        while True:
            try:
                line = input(f"\n{BOLD}›{RESET} ")
            except (EOFError, KeyboardInterrupt):
                print()
                break

            intent = parse(line)
            try:
                if isinstance(intent, Quit):
                    break
                if isinstance(intent, Advance):
                    for _ in range(intent.count):
                        self.show(self.mano.tick())
                elif isinstance(intent, Inject):
                    self.senses.inject(intent.sense, intent.signal)
                    self.show(self.mano.tick())
                elif isinstance(intent, Speech):
                    self.senses.inject(Sense.EAR, intent.text, extra=("form:speech",))
                    self.show(self.mano.tick())
                elif isinstance(intent, Command):
                    self.command(intent.name, intent.args)
            except _Rollback:
                pass
            except Exception as exc:
                print(f"  {RED}{type(exc).__name__}:{RESET} {exc}")

        self.stop_auto()
        self.senses.close()
        print(f"{DIM}the stream continues in {self.store.path}{RESET}")


class _Rollback(Exception):
    """Raised to abandon a tick opened only to look at it. 看不是活."""
