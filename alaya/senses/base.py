"""根 (indriya) — the faculties, and the inbox every one of them carries.

The doctrine distinguishes 識 (the consciousness) from 根 (the faculty it
depends on): 眼識 arises *in dependence on* 眼根. A faculty is not the seeing,
it is the organ that makes seeing possible. So these classes are called
faculties, and what they produce is a :class:`~alaya.senses.Percept`.

DORMANCY IS NOT FAILURE
-----------------------
Three of the five faculties here have no device. That is a perfectly ordinary
condition, not an error state: the doctrine has a name for consciousness with
sense activity absent — 無心位, the mindless states (deep sleep, 悶絕, 滅盡定).
Indeed the whole reason the 阿賴耶識 was posited was to explain how karma
carries *through* such gaps. A dormant faculty returns ``None`` and the stream
continues.

WHY EVERY FACULTY HAS AN INBOX
------------------------------
``gather()`` is a pull. Real sensors push — a BLE characteristic notifies, an
MQTT topic publishes, a websocket frame lands, a human types "you smell pizza".
Rather than inventing a second faculty type for push feeds, every faculty
carries a thread-safe inbox. A bridge running in any thread calls ``inject()``;
the next tick drains it. Adding a Bluetooth sensor therefore requires no new
class and no change here — see ``tests/test_senses.py`` for the pattern.
"""
from __future__ import annotations

import threading
from collections import deque
from typing import NamedTuple

from alaya.senses.percept import Percept, Sense, Source, now


class Reading(NamedTuple):
    """What a live faculty hands back: a signal, optional media, optional tags."""

    signal: str
    media: str | None = None
    extra: tuple[str, ...] = ()


class Faculty:
    """Base for all five. Subclass and override ``available`` and ``sense_now``."""

    sense: Sense = None  # type: ignore[assignment]

    def __init__(self, sense: Sense | None = None):
        if sense is not None:
            self.sense = sense
        self._inbox: deque[Percept] = deque()
        self._lock = threading.Lock()
        self._failed = False

    # ── the live feed ────────────────────────────────────────────────

    @property
    def available(self) -> bool:
        """Whether this faculty has a device path that has not failed.

        Deliberately does *not* probe the hardware. Asking "is the camera
        there?" by opening the camera would trip a permission prompt every time
        anything wanted to render a status line.
        """
        return False

    def sense_now(self) -> Reading | str | None:
        """Take one reading. Override this; return ``None`` for nothing to report."""
        return None

    def gather(self) -> Percept | None:
        """One arising of this faculty, or ``None`` if it did not arise."""
        if not self.available:
            return None
        reading = self.sense_now()
        if reading is None:
            return None
        if isinstance(reading, str):
            reading = Reading(reading)
        return Percept(
            sense=self.sense,
            at=now(),
            signal=reading.signal,
            source=Source.SENSED,
            media=reading.media,
            extra=tuple(reading.extra),
        )

    def close(self) -> None:
        """Release any device. Safe to call on a faculty that never opened one."""

    # ── the push feed ────────────────────────────────────────────────

    def inject(
        self,
        signal: str,
        source: Source = Source.INJECTED,
        extra: tuple[str, ...] = (),
    ) -> Percept:
        """Place a percept in this faculty from outside. Thread-safe.

        ``source`` defaults to INJECTED because the common case is a human at
        the console. A hardware bridge pushing genuine readings should pass
        ``Source.SENSED`` — it *is* a device, it just speaks first rather than
        waiting to be asked.
        """
        percept = Percept(
            sense=self.sense, at=now(), signal=signal, source=source, extra=tuple(extra)
        )
        with self._lock:
            self._inbox.append(percept)
        return percept

    def drain(self) -> list[Percept]:
        """Take everything pushed since the last drain. Thread-safe."""
        with self._lock:
            drained = list(self._inbox)
            self._inbox.clear()
        return drained


class DormantFaculty(Faculty):
    """A faculty with no device — 無心位 for that sense. Injection still works."""

    @property
    def available(self) -> bool:
        return False
