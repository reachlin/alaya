"""耳識 — the ear consciousness. A microphone, reporting sound.

SILENCE IS SOMETHING HEARD
--------------------------
This faculty returns a percept even when nothing is audible, tagged
``level:silent``. That is not padding. 耳識 arising and finding no sound is
still 耳識 arising — an absence *registered* is different in kind from a sense
that did not operate, and only the second is 無心位. Downstream layers can
filter silence; they cannot reconstruct the difference if the ear discards it.

WHERE SPEECH RECOGNITION SITS — THE INTERESTING PROBLEM
-------------------------------------------------------
Strictly, a transcript is not 現量. Hearing *sound* is 耳識 and direct. Hearing
*words* is already 分別 — the 五俱意識 in its second moment, where the doctrine
says cognition "becomes 比量 or 非量". A speech-to-text model is a fallible
discriminator: it can and does mishear, which is precisely what a direct
perception cannot do.

Being rigorous about this would mean emitting two percepts and a claim. Being
useless about it would mean pretending the transcript is raw sound. The
compromise taken here: the ear emits **one** percept carrying the transcript,
tagged ``form:speech`` — and :mod:`alaya.mano` reads that tag and perfumes it
as a ``CLAIM`` with ``Pramana.ANUMANA`` rather than as a ``PERCEPT``. The
doctrinal line still gets drawn; it just gets drawn one layer later, where the
seed is actually made. See ``Mano._seed_for`` for the other half.
"""
from __future__ import annotations

from alaya.senses.base import Faculty, Reading
from alaya.senses.percept import Sense

#: Below this RMS the field counts as silent. Roughly room tone on a laptop mic.
DEFAULT_GATE = 0.01


def _default_recorder(window: float, samplerate: int):
    """Record one window of mono float32 audio from the system input."""
    import sounddevice as sd

    frames = int(window * samplerate)
    audio = sd.rec(frames, samplerate=samplerate, channels=1, dtype="float32")
    sd.wait()
    return audio.reshape(-1)


class Ear(Faculty):
    sense = Sense.EAR

    def __init__(
        self,
        window: float = 1.0,
        samplerate: int = 16_000,
        recorder=None,
        transcriber=None,
        gate: float = DEFAULT_GATE,
    ):
        super().__init__()
        self.window = window
        self.samplerate = samplerate
        self.gate = gate
        self._recorder = recorder or (lambda: _default_recorder(window, samplerate))
        self._transcriber = transcriber

    @property
    def available(self) -> bool:
        return not self._failed

    def sense_now(self) -> Reading | None:
        try:
            audio = self._recorder()
        except Exception:
            # No input device, or permission withheld. The ear is simply shut.
            self._failed = True
            return None
        if audio is None or len(audio) == 0:
            return None

        import numpy as np

        samples = np.asarray(audio, dtype="float32").reshape(-1)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        peak = float(np.max(np.abs(samples)))

        if rms < self.gate:
            # Silence registered — an arising, not an absence of one. The
            # transcriber is deliberately not consulted: asking a speech model
            # to find words in room tone is how phantom transcripts happen,
            # and a phantom transcript is 非量 wearing the costume of 現量.
            return Reading(
                signal=f"{self.window:.1f}s audio · silence (rms {rms:.3f})",
                extra=("level:silent",),
            )

        if self._transcriber is not None:
            try:
                text = self._transcriber(samples, self.samplerate)
            except Exception:
                text = None
            if text and text.strip():
                # Tagged, so mano can record it as the inference it is.
                return Reading(signal=text.strip(), extra=("form:speech",))

        return Reading(signal=f"{self.window:.1f}s audio · rms {rms:.3f} · peak {peak:.3f}")
