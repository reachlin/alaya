"""前五识 — the five faculties, and the field they arise in.

Eye and ear have devices. Nose, tongue and body have none, which is not an
error: a faculty with no feed is dormant, not broken. Every faculty accepts
injection, because a percept placed by a human is still a percept — it is only
its provenance that differs.
"""
import numpy as np
import pytest

from alaya.senses import DormantFaculty, Ear, Eye, Faculty, Percept, Sense, SenseField, Source


# ── fakes standing in for hardware ───────────────────────────────────

class FakeCamera:
    def __init__(self, frames):
        self._frames = list(frames)
        self.released = False

    def read(self):
        if not self._frames:
            return False, None
        return True, self._frames.pop(0)

    def release(self):
        self.released = True


def frame(value, size=(4, 4)):
    return np.full((size[0], size[1], 3), value, dtype=np.uint8)


def recorder_of(*arrays):
    queue = list(arrays)
    return lambda: queue.pop(0) if queue else np.zeros(16, dtype=np.float32)


# ── dormant faculties ────────────────────────────────────────────────

def test_a_dormant_faculty_is_unavailable_not_broken(): 
    nose = DormantFaculty(Sense.NOSE)
    assert nose.available is False
    assert nose.gather() is None


def test_a_dormant_faculty_still_accepts_injection():
    nose = DormantFaculty(Sense.NOSE)
    nose.inject("pizza, cooling")
    (p,) = nose.drain()
    assert p.sense is Sense.NOSE
    assert p.signal == "pizza, cooling"
    assert p.source is Source.INJECTED


# ── 眼识 ─────────────────────────────────────────────────────────────

def test_the_eye_reports_the_signal_not_the_scene():
    """現量 — luminance and motion are properties of the light, not names for it."""
    eye = Eye(opener=lambda: FakeCamera([frame(128)]))
    p = eye.gather()
    assert p.sense is Sense.EYE
    assert "luminance" in p.signal and "4×4" in p.signal
    assert p.source is Source.SENSED


def test_the_eye_measures_luminance():
    bright = Eye(opener=lambda: FakeCamera([frame(255)])).gather()
    dark = Eye(opener=lambda: FakeCamera([frame(0)])).gather()
    assert "1.00" in bright.signal
    assert "0.00" in dark.signal


def test_motion_is_zero_on_the_first_frame_and_positive_on_a_change():
    eye = Eye(opener=lambda: FakeCamera([frame(0), frame(0), frame(255)]))
    assert "motion 0.00" in eye.gather().signal
    assert "motion 0.00" in eye.gather().signal
    assert "motion 0.00" not in eye.gather().signal


def test_an_eye_with_no_camera_is_unavailable_and_yields_nothing():
    def broken():
        raise OSError("no camera")
    eye = Eye(opener=broken)
    assert eye.gather() is None
    assert eye.available is False


def test_an_eye_whose_camera_stops_returning_frames_yields_nothing():
    eye = Eye(opener=lambda: FakeCamera([]))
    assert eye.gather() is None


def test_closing_the_eye_releases_the_device():
    cam = FakeCamera([frame(10)])
    eye = Eye(opener=lambda: cam)
    eye.gather()
    eye.close()
    assert cam.released is True


# ── 耳识 ─────────────────────────────────────────────────────────────

def test_the_ear_reports_acoustic_level():
    ear = Ear(recorder=recorder_of(np.full(160, 0.5, dtype=np.float32)))
    p = ear.gather()
    assert p.sense is Sense.EAR
    assert "rms" in p.signal and "peak" in p.signal


def test_silence_is_still_something_heard():
    """耳识 hearing nothing is still 耳识 arising. It is tagged, not discarded."""
    ear = Ear(recorder=recorder_of(np.zeros(160, dtype=np.float32)))
    p = ear.gather()
    assert p is not None
    assert "level:silent" in p.conditions


def test_sound_above_the_gate_is_not_marked_silent():
    ear = Ear(recorder=recorder_of(np.full(160, 0.5, dtype=np.float32)))
    assert "level:silent" not in ear.gather().conditions


def test_a_transcriber_turns_sound_into_speech_and_says_so():
    """Speech recognition is already 分别 — so the percept is marked as such."""
    ear = Ear(
        recorder=recorder_of(np.full(160, 0.5, dtype=np.float32)),
        transcriber=lambda audio, rate: "is the kettle on",
    )
    p = ear.gather()
    assert p.signal == "is the kettle on"
    assert "form:speech" in p.conditions


def test_a_transcriber_is_not_consulted_for_silence():
    calls = []
    ear = Ear(
        recorder=recorder_of(np.zeros(160, dtype=np.float32)),
        transcriber=lambda a, r: calls.append(1) or "phantom words",
    )
    p = ear.gather()
    assert calls == []
    assert "form:speech" not in p.conditions


def test_an_ear_with_no_microphone_is_unavailable():
    def broken():
        raise OSError("no input device")
    ear = Ear(recorder=broken)
    assert ear.gather() is None
    assert ear.available is False


# ── 五识身 — the field ───────────────────────────────────────────────

def test_the_field_has_all_five_faculties():
    field = SenseField()
    assert set(field.faculties) == set(Sense)


def test_by_default_only_eye_and_ear_have_feeds():
    field = SenseField()
    assert field.available()[Sense.NOSE] is False
    assert field.available()[Sense.TONGUE] is False
    assert field.available()[Sense.BODY] is False


def test_injection_reaches_the_named_sense(): 
    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    field.inject(Sense.NOSE, "pizza")
    (p,) = field.gather()
    assert p.sense is Sense.NOSE and p.signal == "pizza"


def test_an_injected_percept_is_drained_once():
    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    field.inject(Sense.TONGUE, "salt")
    assert len(field.gather()) == 1
    assert field.gather() == []


def test_the_field_gathers_from_devices_and_injections_together():
    field = SenseField(faculties={
        Sense.EYE: Eye(opener=lambda: FakeCamera([frame(64)])),
        Sense.EAR: DormantFaculty(Sense.EAR),
        Sense.NOSE: DormantFaculty(Sense.NOSE),
        Sense.TONGUE: DormantFaculty(Sense.TONGUE),
        Sense.BODY: DormantFaculty(Sense.BODY),
    })
    field.inject(Sense.NOSE, "rain on hot pavement")
    senses = {p.sense for p in field.gather()}
    assert senses == {Sense.EYE, Sense.NOSE}


def test_a_field_of_dormant_faculties_gathers_nothing():
    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    assert field.gather() == []


def test_injected_percepts_come_first():
    """What is already present arises before what must be fetched."""
    field = SenseField(faculties={
        Sense.EYE: Eye(opener=lambda: FakeCamera([frame(64)])),
        **{s: DormantFaculty(s) for s in Sense if s is not Sense.EYE},
    })
    field.inject(Sense.BODY, "a chill")
    assert field.gather()[0].sense is Sense.BODY


def test_a_faculty_that_raises_does_not_take_the_field_down():
    """A sense may fail. 無心位 is a state, not a crash."""
    class Exploding(DormantFaculty):
        @property
        def available(self):
            return True
        def gather(self):
            raise RuntimeError("device on fire")

    field = SenseField(faculties={
        Sense.EYE: Exploding(Sense.EYE),
        **{s: DormantFaculty(s) for s in Sense if s is not Sense.EYE},
    })
    field.inject(Sense.NOSE, "smoke")
    (p,) = field.gather()
    assert p.sense is Sense.NOSE


def test_closing_the_field_closes_every_faculty():
    cam = FakeCamera([frame(1)])
    field = SenseField(faculties={
        Sense.EYE: Eye(opener=lambda: cam),
        **{s: DormantFaculty(s) for s in Sense if s is not Sense.EYE},
    })
    field.gather()
    field.close()
    assert cam.released is True


# ── the extension point — where a Bluetooth sensor will plug in ──────

def test_a_partial_field_fills_the_rest_with_dormant_faculties():
    """Name only the faculties you have; the others are dormant, not missing."""
    field = SenseField(faculties={Sense.NOSE: DormantFaculty(Sense.NOSE)})
    assert set(field.faculties) == set(Sense)
    assert field.available()[Sense.EYE] is False


def test_a_custom_faculty_plugs_in_by_subclassing():
    """Any device — BLE, serial, HTTP — is a Faculty with three members."""
    class Thermometer(Faculty):
        sense = Sense.BODY

        @property
        def available(self):
            return True

        def sense_now(self):
            return "skin 34.2C, ambient 21.0C"

    field = SenseField(faculties={Sense.BODY: Thermometer()})
    (p,) = field.gather()
    assert p.sense is Sense.BODY
    assert "34.2C" in p.signal
    assert p.source is Source.SENSED


def test_a_faculty_accepts_pushes_from_another_thread():
    """A push feed (BLE notify, MQTT, websocket) needs no new faculty type:
    the bridge thread calls inject(), and the tick drains it."""
    import threading

    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    done = threading.Event()

    def bridge():
        for reading in ("co2 812ppm", "co2 640ppm", "co2 511ppm"):
            field.inject(Sense.NOSE, reading)
        done.set()

    threading.Thread(target=bridge).start()
    done.wait(timeout=2)

    signals = [p.signal for p in field.gather()]
    assert signals == ["co2 812ppm", "co2 640ppm", "co2 511ppm"]


def test_pushed_percepts_are_sensed_not_injected_when_marked_so():
    """A real sensor pushing through the same inbox is still 現量 from a device."""
    field = SenseField(faculties={s: DormantFaculty(s) for s in Sense})
    field.inject(Sense.BODY, "34.2C", source=Source.SENSED)
    (p,) = field.gather()
    assert p.source is Source.SENSED
    assert "source:sensed" in p.conditions
