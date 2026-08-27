"""The console — the human end of the stream.

Parsing is a pure function so it can be pinned down here. The rule of thumb:
anything you type that is not addressed to a *sense* is addressed to the agent,
and reaches it through the ear as speech — because that is how speech actually
reaches a mind.
"""
import pytest

from alaya.console import Advance, Command, Inject, Quit, Speech, parse
from alaya.senses import Sense


# ── advancing ────────────────────────────────────────────────────────

@pytest.mark.parametrize("line", ["", "   ", "\t"])
def test_an_empty_line_advances_one_moment(line):
    assert parse(line) == Advance(1)


def test_tick_advances_several(): 
    assert parse("/tick 3") == Advance(3)


def test_tick_with_no_count_advances_one():
    assert parse("/tick") == Advance(1)


# ── injecting into a sense ───────────────────────────────────────────

@pytest.mark.parametrize("line,sense,signal", [
    ("you hear a dog bark", Sense.EAR, "a dog bark"),
    ("you see a red door", Sense.EYE, "a red door"),
    ("you smell pizza", Sense.NOSE, "pizza"),
    ("you taste salt", Sense.TONGUE, "salt"),
    ("you feel cold", Sense.BODY, "cold"),
])
def test_the_second_person_forms_reach_the_named_sense(line, sense, signal):
    assert parse(line) == Inject(sense, signal)


def test_the_second_person_forms_are_case_insensitive():
    assert parse("You Hear A Dog Bark") == Inject(Sense.EAR, "A Dog Bark")


@pytest.mark.parametrize("line,sense", [
    ("/hear a dog bark", Sense.EAR),
    ("/see a red door", Sense.EYE),
    ("/smell pizza", Sense.NOSE),
    ("/taste salt", Sense.TONGUE),
    ("/feel cold", Sense.BODY),
])
def test_the_slash_forms_reach_the_named_sense(line, sense):
    assert parse(line).sense is sense


def test_smelled_and_smells_are_accepted_too():
    assert parse("you smelled smoke") == Inject(Sense.NOSE, "smoke")
    assert parse("you hears a bell") == Inject(Sense.EAR, "a bell")


def test_an_empty_injection_is_not_an_injection():
    assert parse("/smell") != Inject(Sense.NOSE, "")
    assert isinstance(parse("/smell"), Command)


# ── speech ───────────────────────────────────────────────────────────

def test_anything_else_is_heard_as_speech():
    assert parse("hello, are you there") == Speech("hello, are you there")


def test_a_sentence_that_merely_mentions_a_sense_is_still_speech():
    assert parse("can you hear me") == Speech("can you hear me")


# ── commands ─────────────────────────────────────────────────────────

def test_a_bare_command():
    assert parse("/status") == Command("status", ())


def test_a_command_with_arguments():
    assert parse("/recall the kettle") == Command("recall", ("the", "kettle"))


@pytest.mark.parametrize("line", ["/quit", "/exit", "/q"])
def test_quitting(line):
    assert parse(line) == Quit()


def test_an_unknown_command_is_still_a_command():
    """Better a command that reports itself unknown than text sent to the ear."""
    assert parse("/wibble") == Command("wibble", ())
