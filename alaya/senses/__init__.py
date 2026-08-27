"""前五識 — the five sense consciousnesses.

    眼識 :class:`Eye`      camera — luminance, motion, and the frame itself
    耳識 :class:`Ear`      microphone — level, and speech when a transcriber is set
    鼻識 :class:`DormantFaculty`   no device yet
    舌識 :class:`DormantFaculty`   no device yet
    身識 :class:`DormantFaculty`   no device yet

All five accept injection, so the three without devices are still usable from
the console ("you smell pizza") and are where a Bluetooth or serial sensor will
attach without any new faculty type. See :mod:`alaya.senses.base`.

The governing constraint of this package is 唯現量: these report signals, never
names. See :mod:`alaya.senses.percept` for why that line is load-bearing.
"""
from alaya.senses.base import DormantFaculty, Faculty, Reading
from alaya.senses.ear import Ear
from alaya.senses.eye import Eye
from alaya.senses.field import SenseField
from alaya.senses.percept import Percept, Sense, Source, now

__all__ = [
    "DormantFaculty", "Ear", "Eye", "Faculty", "Percept",
    "Reading", "Sense", "SenseField", "Source", "now",
]
