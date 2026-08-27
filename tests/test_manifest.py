"""變現 — the world is a projection from the store, not the sensor feed.

阿賴耶識 變現根身器世間. What the sixth consciousness deliberates over is never
raw intake: it is a world assembled out of seeds that the present conditions
caused to arise. Retrieval is world-construction.
"""
from alaya.manifest import Body, World, manifest
from alaya.senses import Percept, Sense, Source
from alaya.seeds import Kind, Nature, Valence
from tests.conftest import percept as seed_of


def p(sense, signal, source=Source.SENSED, extra=()):
    return Percept(sense=sense, at="t", signal=signal, source=source, extra=extra)


def test_present_conditions_come_from_the_percepts(store):
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={}, tools=())
    assert world.conditions == frozenset({"sense:ear", "source:sensed"})


def test_seeds_whose_conditions_are_met_appear_in_the_world(store):
    with store.tick() as t:
        remembered = seed_of(t, "the kettle whistles before it boils", conditions=("sense:ear",))
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={}, tools=())
    assert world.active == (remembered,)


def test_seeds_whose_conditions_are_absent_do_not(store):
    with store.tick() as t:
        seed_of(t, "the porch light is on", conditions=("sense:eye",))
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={}, tools=())
    assert world.active == ()


def test_the_world_of_an_empty_store_is_the_bare_present(store):
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={}, tools=())
    assert world.active == ()
    assert len(world.percepts) == 1


def test_extra_conditions_widen_what_arises(store):
    """Volition can add conditions — 作意, attention as a condition of arising."""
    with store.tick() as t:
        seed_of(t, "she said she'd call at six", conditions=("topic:call",))
    with store.tick() as t:
        world = manifest(t, [], senses={}, tools=(), extra_conditions=("topic:call",))
    assert [s.content for s in world.active] == ["she said she'd call at six"]


def test_the_body_reports_which_faculties_have_a_feed(store):
    """根身 — the agent's own body, manifested from the same store."""
    with store.tick() as t:
        world = manifest(
            t, [], senses={Sense.EYE: True, Sense.NOSE: False}, tools=("speak", "remember")
        )
    assert world.body.senses[Sense.EYE] is True
    assert world.body.senses[Sense.NOSE] is False
    assert world.body.tools == ("speak", "remember")
    assert world.body.tick == t.number


def test_render_shows_the_percepts_and_the_arisen_seeds(store):
    with store.tick() as t:
        seed_of(t, "the kettle whistles before it boils", conditions=("sense:ear",))
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={Sense.EAR: True}, tools=("speak",))
    text = world.render()
    assert "a rising tone" in text
    assert "the kettle whistles before it boils" in text
    assert str(t.number) in text


def test_render_marks_injected_percepts_as_injected(store):
    with store.tick() as t:
        world = manifest(t, [p(Sense.NOSE, "pizza", source=Source.INJECTED)], senses={}, tools=())
    assert "injected" in world.render()


def test_render_says_plainly_when_nothing_arose(store):
    with store.tick() as t:
        world = manifest(t, [], senses={}, tools=())
    assert "nothing" in world.render().lower()


def test_images_are_offered_separately_from_the_text(store):
    """The frame goes to the model as an image, not as a sentence about an image."""
    eye = Percept(sense=Sense.EYE, at="t", signal="frame 4×4 · luminance 0.5", media="BASE64")
    with store.tick() as t:
        world = manifest(t, [eye], senses={}, tools=())
    assert world.images == ("BASE64",)


def test_activation_in_the_world_is_recorded_for_provenance(store):
    """What the world was built from is exactly what a later act may cite."""
    with store.tick() as t:
        remembered = seed_of(t, "the kettle whistles", conditions=("sense:ear",))
    with store.tick() as t:
        world = manifest(t, [p(Sense.EAR, "a rising tone")], senses={}, tools=())
        act = t.perfume(
            content="checked the kettle", kind=Kind.ACT, valence=Valence.NEUTRAL,
            nature=Nature.PARATANTRA, parents=[s.id for s in world.active],
        )
    assert remembered in store.trace(act.id)
