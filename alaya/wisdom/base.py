"""轉依 — the basis, and what a transformation of it reports.

轉依 (āśraya-parāvṛtti) is the technical term for the whole project of
轉識成智: not the removal of the eight consciousnesses but a turning of the
所依, the basis they run on. The same faculties, no longer organised around
自我. Nothing is deleted — which is the same shape as the store's own rule, and
not a coincidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from alaya.directive import Directive
    from alaya.manas import Manas
    from alaya.providers import Provider
    from alaya.seeds import SeedStore
    from alaya.senses import SenseField


class UntimelyError(RuntimeError):
    """A 果上圓 transformation attempted while the stream is still running."""


class Stage(str, Enum):
    """When a given consciousness can turn — 六七因中轉，五八果上圓.

    The doctrine's reason is precise: 分別 and 我執 are reachable by wisdom
    directly, so the sixth and seventh begin to turn at 見道 (初地) while
    practice is still under way. The five senses and the store need both
    obstructions gone, and are perfected only at the fruit.

    As engineering: prompt and self-model can be revised from the agent's own
    trace while it runs, cheaply, every cycle. Sensors and substrate need the
    stream stopped and a batch pass over everything. The doctrine's timing rule
    *is* the correct split, and it is enforced rather than described.
    """

    CAUSE = "因中轉"   # online, during practice — the sixth and seventh
    FRUIT = "果上圓"   # offline, on completion — the five senses and the store


@dataclass
class Basis:
    """所依 — everything a turning may act upon.

    Every part but the store is optional. A transformation with nothing to act
    on measures itself and reports no change, which is the honest outcome
    rather than an error: an agent with no self-model has no 我執 to correct.
    """

    store: "SeedStore"
    manas: "Manas | None" = None
    senses: "SenseField | None" = None
    directive: "Directive | None" = None
    provider: "Provider | None" = None


@dataclass(frozen=True)
class Progress:
    """How far one transformation has come. Never 1.0 in practice.

    The dashed lines in the source diagram are 尚未圓滿的轉依 — transformations
    under way and not complete. This dataclass is those dashed lines: a score
    that should move, not a box that gets ticked.
    """

    wisdom: str      # 妙觀察智
    roman: str       # discerning
    layer: str       # 第六意識
    stage: Stage
    score: float
    metrics: dict = field(default_factory=dict)
    notes: tuple[str, ...] = ()
    changed: bool = False

    def render(self) -> str:
        bar = "█" * round(self.score * 12)
        rail = "┄" * (12 - len(bar))    # ┄ — the transformation not yet complete
        mark = " ·turned" if self.changed else ""
        lines = [f"  {self.layer:<12} → {self.wisdom}  {bar}{rail} {self.score:>4.0%}"
                 f"  [{self.stage.value}]{mark}"]
        lines += [f"      {n}" for n in self.notes]
        return "\n".join(lines)


@dataclass(frozen=True)
class Turning:
    stage: Stage | None
    progress: tuple[Progress, ...]

    @property
    def score(self) -> float:
        return sum(p.score for p in self.progress) / len(self.progress) if self.progress else 0.0

    def render(self) -> str:
        head = f"轉識成智 — {self.stage.value if self.stage else 'all four'}"
        body = "\n".join(p.render() for p in self.progress)
        return f"{head}\n{body}\n  {'─' * 46}\n  轉依 overall {self.score:.0%} — 尚未圓滿"


class Wisdom(Protocol):
    wisdom: str
    roman: str
    layer: str
    stage: Stage

    def measure(self, basis: Basis) -> Progress: ...
    def turn(self, basis: Basis) -> Progress: ...
