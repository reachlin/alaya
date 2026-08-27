"""現量 — bare intake, and the type that refuses to hold more than that.

WHAT THE DOCTRINE SAYS
----------------------
The 前五識 (pañca-vijñāna — eye, ear, nose, tongue, body consciousness) are
唯現量: *direct perception only*. 現量 (pratyakṣa) is defined by three
conditions — the object must be **present** (not remembered or anticipated),
**manifest** (actually arisen, not still latent as a seed), and **clear** to
both the knowing and the known side. Crucially it is 無分別: unmixed with
discrimination, and 不帶名言 — carrying no verbal label.

That last clause is the one this module enforces. The eye does not see "a dog".
The eye receives light. "A dog" is a *name*, and naming is the work of the
第六意識, which is 通三量 — it can be direct, but it can equally infer (比量)
or err (非量). The instant you record "a dog" as though the eye had delivered
it, you have laundered a fallible judgment into an infallible observation, and
nothing downstream can tell the difference any more.

HOW THAT BECOMES A TYPE
-----------------------
:class:`Percept` has a ``signal`` and no ``label``. It has no ``meaning``, no
``description``, no ``objects``, no ``caption``. There is nowhere to put the
interpretation, so the interpretation must be made somewhere it can be tagged
with the measure of knowledge that produced it. ``tests/test_percept.py``
asserts the absence of those field names, so the constraint cannot rot.

A NOTE ON 五俱意識
-----------------
The doctrine is subtler than "senses are dumb". 五俱意識 (the mind-consciousness
that co-arises with the senses) accompanies every sense act and is *also*
classed as 現量 in its first moment — but "in the second moment it has
discrimination, becoming 比量 or 非量". The boundary this module draws is
exactly that first/second moment line: everything up to and including the
signal is 現量; the second moment happens in :mod:`alaya.mano`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Sense(str, Enum):
    """前五識 — the five sense consciousnesses, in their traditional order."""

    EYE = "eye"        # 眼識 — cakṣur-vijñāna
    EAR = "ear"        # 耳識 — śrotra-vijñāna
    NOSE = "nose"      # 鼻識 — ghrāṇa-vijñāna
    TONGUE = "tongue"  # 舌識 — jihvā-vijñāna
    BODY = "body"      # 身識 — kāya-vijñāna


class Source(str, Enum):
    """Where a percept came from.

    Not a doctrinal category — the doctrine has no notion of a human typing at
    a console. It is here because provenance matters more for an injected
    percept than for a sensed one: the agent cannot tell the difference from
    the inside (both simply arise), but anyone reading ``trace()`` afterwards
    should be able to.
    """

    SENSED = "sensed"      # a device delivered it
    INJECTED = "injected"  # a human placed it, or a bridge pushed it


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Percept:
    """One arising of one sense consciousness.

    ``signal`` describes the *signal* — "frame 1280×720 · luminance 0.42 ·
    motion 0.11", "1.0s audio · rms 0.08 · peak 0.34". Never the scene. If you
    find yourself wanting to write a sentence about what is in the picture,
    that sentence belongs in a :class:`~alaya.seeds.Seed` of kind ``CLAIM``
    with a :class:`~alaya.seeds.Pramana` attached, not here.
    """

    sense: Sense
    at: str
    signal: str
    source: Source = Source.SENSED
    media: str | None = None        # base64 frame, audio blob — uninterpreted
    extra: tuple[str, ...] = field(default_factory=tuple)

    @property
    def conditions(self) -> tuple[str, ...]:
        """待眾緣 tags — the conditions this arising contributes to the moment.

        These are what cause stored seeds to fire. A seed perfumed under
        ``sense:ear`` will arise again the next time the ear does, which is the
        whole mechanism by which a memory becomes relevant without anyone
        querying for it.
        """
        return tuple(sorted({
            f"sense:{self.sense.value}",
            f"source:{self.source.value}",
            *self.extra,
        }))
