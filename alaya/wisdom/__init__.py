"""轉識成智 — the four transformations, and the rule about when each happens.

    前五識 → 成所作智  accomplishing      果上圓 · offline, batch
    第六識 → 妙觀察智  discerning         因中轉 · online, every cycle
    第七識 → 平等性智  equality           因中轉 · online, every cycle
    第八識 → 大圓鏡智  mirror             果上圓 · offline, batch

六七因中轉，五八果上圓. The sixth and seventh begin turning at 見道, while
practice is under way, because 分別 and 我執 are what wisdom can reach directly.
The five senses and the store are perfected only at the fruit, once both
obstructions are gone — they cannot be corrected from inside their own
operation.

That is also, exactly, the right engineering split: prompt and self-model are
cheap and revisable from the agent's own trace while it runs; sensors and
substrate need the stream stopped and a pass over everything. It is enforced
here, not merely described — a 果上圓 turning raises :class:`UntimelyError` if
attempted mid-tick.

    turn(basis, Stage.CAUSE)   # cheap, safe to run constantly
    turn(basis, Stage.FRUIT)   # expensive, requires a quiet stream
    measure(basis)             # all four, changes nothing, always allowed
"""
from alaya.wisdom.accomplishing import Accomplishing
from alaya.wisdom.base import (
    Basis,
    Progress,
    Stage,
    Turning,
    UntimelyError,
    Wisdom,
)
from alaya.wisdom.discerning import Discerning
from alaya.wisdom.equality import Equality
from alaya.wisdom.mirror import Mirror

__all__ = [
    "Accomplishing", "Basis", "Discerning", "Equality", "Mirror", "Progress",
    "Stage", "Turning", "UntimelyError", "Wisdom", "measure", "turn", "WISDOMS",
]

#: The four, in the order the 八識規矩頌 treats them.
WISDOMS: tuple = (Accomplishing, Discerning, Equality, Mirror)


def _instances(stage: Stage | None = None) -> list:
    return [w() for w in WISDOMS if stage is None or w.stage is stage]


def measure(basis: Basis) -> Turning:
    """Report all four without changing anything.

    Always permitted, including mid-tick. Looking is not turning: 果上圓
    restricts the transformation, never the metric.
    """
    return Turning(stage=None, progress=tuple(w.measure(basis) for w in _instances()))


def turn(basis: Basis, stage: Stage = Stage.CAUSE) -> Turning:
    """Perform the transformations belonging to one stage.

    They do not all turn together, and pretending otherwise would lose the most
    useful thing the doctrine says about this: that some improvements are cheap
    and continuous while others require stopping.
    """
    if stage is Stage.FRUIT and basis.store.ticking:
        raise UntimelyError(
            "果上圓 — the five senses and the store are perfected at the fruit, not "
            "during practice. A moment is still open; this turning needs a settled "
            "store to see."
        )
    return Turning(stage=stage, progress=tuple(w.turn(basis) for w in _instances(stage)))
