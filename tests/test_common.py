"""共業 — why two beings see the same mountain.

THE OBJECTION THIS ANSWERS
If everything is 唯識, why do you and I see the same river? The obvious reading
— that one of us is hallucinating, or that there is after all a river out there
independent of any mind — is exactly what 唯識 refuses. Its own answer is 共業:
the 器世間 is 共變, collectively transformed, manifested congruently by beings
whose karma is shared.

This is the school's defence against being read as solipsism, and it is not an
afterthought — 《唯識二十論》 takes 多人共見 (many people seeing the same thing) as
one of the four strongest objections and answers it here. An implementation that
skipped 共業 would leave 唯識 looking like private hallucination, which is the
misreading the source text spends its opening refuting.

WHAT IT IS NOT
There is no shared store. The ālaya is **individual** — each being has one, and
a universal mind is a different doctrine belonging to a different school. So
this module never gives two agents one store. Each keeps its own, and what
passes between them is 共相種子, common seeds: immutable records that each agent
perfumes into its own stream and manifests for itself.

The worlds look alike because the seeds are alike. Not because there is one
world object they are both pointed at. That distinction is the whole doctrine,
and it happens to be the better distributed-systems design too: no shared
mutable state, only propagation of content-addressed records.

不共 — WHAT NEVER TRAVELS
The classical division is 共 and 不共, and 根身 — one's own embodied faculties —
is 不共業所感, manifested by karma that is one's own alone. So percepts do not
travel. What your eye did is not something anyone else can be given; only what
you made of it can be.
"""
import pytest

from alaya.common import Commons, Offering
from alaya.seeds import Kind, Nature, Pramana, SeedStore, Valence
from tests.conftest import percept as seed_of


@pytest.fixture
def commons(tmp_path):
    return Commons(tmp_path / "commons.jsonl")


@pytest.fixture
def other(tmp_path):
    return SeedStore(tmp_path / "other.jsonl")


def claim(t, content, nature=Nature.PARATANTRA, pramana=Pramana.ANUMANA,
          valence=Valence.NEUTRAL, conditions=()):
    return t.perfume(content=content, kind=Kind.CLAIM, valence=valence,
                     nature=nature, pramana=pramana, conditions=conditions)


# ── 不共 — what never leaves ─────────────────────────────────────────

def test_percepts_are_never_offered(store, commons):
    """根身 is 不共業所感 — what your own faculty presented is yours alone."""
    with store.tick() as t:
        seed_of(t, "1.0s audio · rms 0.4", conditions=("sense:ear",))
    assert commons.offer(store, "a") == []


def test_reflections_are_never_offered(store, commons):
    with store.tick() as t:
        t.perfume(content="felt uneasy", kind=Kind.REFLECTION, valence=Valence.NEUTRAL,
                  nature=Nature.PARATANTRA)
    assert commons.offer(store, "a") == []


def test_a_private_condition_is_stripped_before_travelling(store, commons):
    """Which of *your* faculties presented it is 不共 even when the claim is 共."""
    with store.tick() as t:
        claim(t, "the kettle is boiling", conditions=("sense:ear", "topic:kitchen"))
    (offering,) = commons.offer(store, "a")
    assert "topic:kitchen" in offering.conditions
    assert not any(c.startswith("sense:") for c in offering.conditions)


# ── 共 — what does travel ────────────────────────────────────────────

def test_a_borne_claim_is_offered(store, commons):
    with store.tick() as t:
        claim(t, "the kettle is boiling", conditions=("topic:kitchen"[:0] or "topic:kitchen",))
    (offering,) = commons.offer(store, "a")
    assert offering.content == "the kettle is boiling"
    assert offering.origin == "a"


def test_acts_are_offered(store, commons):
    """不共中共 — your own doing, which others can nonetheless come to know of."""
    with store.tick() as t:
        t.perfume(content="turned off the stove", kind=Kind.ACT, valence=Valence.NEUTRAL,
                  nature=Nature.PARATANTRA)
    assert [o.content for o in commons.offer(store, "a")] == ["turned off the stove"]


def test_fabrication_does_not_travel_by_default(store, commons):
    """A design choice, and a departure from the doctrine — see the module."""
    with store.tick() as t:
        claim(t, "my neighbour left it", nature=Nature.PARIKALPITA,
              pramana=Pramana.APRAMANA)
    assert commons.offer(store, "a") == []


def test_fabrication_travels_when_the_commons_is_told_to_allow_it(store, tmp_path):
    """共業 in the doctrine explains shared delusion as readily as shared rivers."""
    commons = Commons(tmp_path / "c.jsonl", only_borne=False)
    with store.tick() as t:
        claim(t, "my neighbour left it", nature=Nature.PARIKALPITA,
              pramana=Pramana.APRAMANA)
    assert len(commons.offer(store, "a")) == 1


def test_offering_twice_does_not_duplicate(store, commons):
    with store.tick() as t:
        claim(t, "the kettle is boiling")
    assert len(commons.offer(store, "a")) == 1
    assert commons.offer(store, "a") == []


# ── receiving ────────────────────────────────────────────────────────

def _shared(store, commons, content="the kettle is boiling", **kw):
    with store.tick() as t:
        claim(t, content, **kw)
    return commons.offer(store, "a")


def test_receiving_perfumes_a_seed_of_ones_own(store, other, commons):
    """各自變現 — B does not get A's seed. B makes one."""
    _shared(store, commons)
    (received,) = commons.receive(other, "b")
    assert received.content == "the kettle is boiling"
    assert received in other.all()
    assert received not in store.all()


def test_nothing_another_agent_says_is_ever_direct_perception(store, other, commons):
    """You did not see it. At best you infer from the fact that they said so."""
    _shared(store, commons)
    (received,) = commons.receive(other, "b")
    assert received.pramana is Pramana.ANUMANA
    assert received.pramana is not Pramana.PRATYAKSA


def test_a_received_seed_records_who_it_came_from(store, other, commons):
    _shared(store, commons)
    (received,) = commons.receive(other, "b")
    assert "from:a" in received.conditions


def test_a_received_seed_keeps_the_conditions_that_let_it_arise(store, other, commons):
    """It has to fire in B's world, or sharing it accomplished nothing."""
    _shared(store, commons, conditions=("topic:kitchen",))
    commons.receive(other, "b")
    assert other.activate({"topic:kitchen", "from:a"})


def test_a_received_seed_keeps_its_valence(store, other, commons):
    """性決定 — a wholesome seed does not sour in transit."""
    _shared(store, commons, content="she helped him", valence=Valence.WHOLESOME)
    (received,) = commons.receive(other, "b")
    assert received.valence is Valence.WHOLESOME


def test_receiving_twice_does_not_duplicate(store, other, commons):
    _shared(store, commons)
    assert len(commons.receive(other, "b")) == 1
    assert commons.receive(other, "b") == []


def test_an_agent_does_not_receive_its_own_offerings(store, commons):
    _shared(store, commons)
    assert commons.receive(store, "a") == []


def test_what_was_received_is_not_offered_onward(store, other, commons):
    """Otherwise two agents echo one claim between them forever."""
    _shared(store, commons)
    commons.receive(other, "b")
    assert commons.offer(other, "b") == []


# ── the point of the whole thing ─────────────────────────────────────

def test_two_agents_come_to_share_a_world_without_sharing_a_store(store, other, commons):
    with store.tick() as t:
        seed_of(t, "1.0s audio · rms 0.4", conditions=("sense:ear",))
        claim(t, "the kettle is boiling", conditions=("topic:kitchen",))
    commons.offer(store, "a")
    commons.receive(other, "b")

    # B knows the kettle is boiling…
    assert any("kettle" in s.content for s in other.all())
    # …and has no access whatever to A's hearing of it. 根身 is 不共.
    assert not any("rms" in s.content for s in other.all())
    # Two stores, two files, no shared object between them.
    assert store.path != other.path


def test_the_commons_survives_reopening(store, other, tmp_path):
    path = tmp_path / "commons.jsonl"
    _shared(store, Commons(path))
    assert len(Commons(path).receive(other, "b")) == 1


def test_an_empty_commons_gives_nothing(other, commons):
    assert commons.receive(other, "b") == []


def test_offerings_round_trip_through_the_file(store, commons):
    _shared(store, commons)
    (raw,) = commons.offerings()
    assert isinstance(raw, Offering)
    assert raw.origin == "a"


def test_a_received_seed_carries_no_condition_nothing_can_present(store, other, commons):
    """待眾緣 — conditions are requirements for *arising*. A bookkeeping hash in
    there is a requirement no moment can ever meet, and the seed is inert."""
    _shared(store, commons, conditions=("topic:kitchen",))
    (received,) = commons.receive(other, "b")
    assert all(":" not in c or not c.split(":", 1)[1].strip("0123456789abcdef") == ""
               or c.startswith(("topic:", "from:")) for c in received.conditions)
    # the real test: presenting only what a world could actually present fires it
    assert other.activate(set(received.conditions)) == [received]
