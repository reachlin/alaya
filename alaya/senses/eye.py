"""眼識 — the eye consciousness. A camera, reporting light and nothing else.

WHAT THIS FILE REFUSES TO DO
----------------------------
It has a frame. It could describe the frame. It does not, and that restraint is
the entire point of the file.

眼識 is 唯現量 — direct perception only, 無分別, 不帶名言. It presents colour and
form; it does not present *objects*, because an object is a name and names are
the sixth consciousness's business. So this faculty reports three numbers that
are genuinely properties of the light itself:

    luminance   mean intensity, 0..1 — how bright the field is
    motion      mean absolute difference from the previous frame, 0..1
    dimensions  the extent of the field

The frame itself travels on as ``media``, uninterpreted. When a vision model
later looks at it and says "a person at a desk", that becomes a CLAIM seed with
``Pramana.ANUMANA`` — an inference, defeasible, tagged as such — rather than an
observation that can never be questioned. Everything downstream depends on that
line being drawn *here*, because after this point the information about who
did the naming is gone.
"""
from __future__ import annotations

import base64

from alaya.senses.base import Faculty, Reading
from alaya.senses.percept import Sense


def _default_opener(index: int):
    """Open the system camera through OpenCV's AVFoundation/V4L2 backend."""
    import cv2

    device = cv2.VideoCapture(index)
    if not device.isOpened():
        device.release()
        raise OSError(f"no camera at index {index}")
    return device


class Eye(Faculty):
    sense = Sense.EYE

    def __init__(self, index: int = 0, opener=None):
        super().__init__()
        self._index = index
        self._opener = opener or (lambda: _default_opener(index))
        self._device = None
        self._previous = None  # the last frame, for the motion difference

    @property
    def available(self) -> bool:
        return not self._failed

    def sense_now(self) -> Reading | None:
        device = self._open()
        if device is None:
            return None

        ok, frame = device.read()
        if not ok or frame is None:
            # A dropped frame is a blink, not a blinding. The device stays live.
            return None

        height, width = frame.shape[0], frame.shape[1]
        luminance = float(frame.mean()) / 255.0

        # 現量 has no memory — but *motion* is a property of the present light
        # field only if you have the previous one to compare against. This is
        # the one place the faculty holds state, and it holds a frame, never a
        # judgment about the frame.
        motion = 0.0
        if self._previous is not None and self._previous.shape == frame.shape:
            import numpy as np

            motion = float(np.abs(frame.astype("int16") - self._previous.astype("int16")).mean()) / 255.0
        self._previous = frame

        return Reading(
            signal=f"frame {width}×{height} · luminance {luminance:.2f} · motion {motion:.2f}",
            media=self._encode(frame),
        )

    def close(self) -> None:
        if self._device is not None:
            try:
                self._device.release()
            except Exception:
                pass
            self._device = None

    # ── internals ────────────────────────────────────────────────────

    def _open(self):
        if self._device is not None:
            return self._device
        if self._failed:
            return None
        try:
            self._device = self._opener()
        except Exception:
            # No camera, or macOS withheld permission. The eye is simply shut.
            self._failed = True
            return None
        return self._device

    @staticmethod
    def _encode(frame) -> str | None:
        """JPEG the frame for a vision model. Still not an interpretation."""
        try:
            import cv2

            ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            return base64.b64encode(buffer).decode("ascii") if ok else None
        except Exception:
            return None
