"""現量 — bare intake.

The five sense consciousnesses present; they do not name. A percept carries a
description of the *signal* and nothing about what the signal is *of*. The
moment something is called "a dog" it has passed into the sixth consciousness
and become a claim, with a nature that can be examined.
"""
import dataclasses

import pytest

from alaya.senses import Percept, Sense, Source


def test_a_percept_has_no_place_to_put_an_interpretation():
    """現量 enforced by the type: there is nowhere to write a meaning."""
    fields = {f.name for f in dataclasses.fields(Percept)}
    forbidden = {"label", "meaning", "interpretation", "description",
                 "objects", "tags", "summary", "caption"}
    assert fields & forbidden == set()


def test_a_percept_is_frozen():
    p = Percept(sense=Sense.EAR, at="2026-08-27T00:00:00+00:00", signal="0.5s audio · rms 0.02")
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.signal = "a dog barking"


def test_conditions_carry_the_sense_and_the_source():
    p = Percept(sense=Sense.NOSE, at="t", signal="burnt sugar", source=Source.INJECTED)
    assert p.conditions == ("sense:nose", "source:injected")


def test_extra_conditions_are_merged_and_sorted():
    p = Percept(sense=Sense.EAR, at="t", signal="hello", extra=("form:speech",))
    assert p.conditions == ("form:speech", "sense:ear", "source:sensed")


def test_sensed_is_the_default_source():
    assert Percept(sense=Sense.EYE, at="t", signal="x").source is Source.SENSED


def test_injected_percepts_are_marked_as_such():
    """An injected percept is a real percept — but its provenance says who placed it."""
    p = Percept(sense=Sense.NOSE, at="t", signal="pizza", source=Source.INJECTED)
    assert "source:injected" in p.conditions
    assert "source:sensed" not in p.conditions


def test_media_is_carried_uninterpreted():
    p = Percept(sense=Sense.EYE, at="t", signal="frame 4×4 · luminance 0.50", media="AAAA")
    assert p.media == "AAAA"
    assert "luminance" in p.signal
