"""第八阿赖耶识 — the seed store and its six criteria.

種子六義, as invariants rather than commentary:

    刹那灭  seeds are frozen and content-addressed; there is no update, no delete
    果俱有  a seed's parents must be present in the same tick that bore it
    恒随转  nothing is removed; strength decays toward a floor above zero
    性决定  valence is fixed at write; derived seeds keep their parents' nature
    待众缘  a seed fires only when all of its conditions are present
    引自果  every parent resolves, and ``trace`` walks the whole ancestry
"""
from alaya.seeds.perfume import Tick
from alaya.seeds.seed import (
    Kind,
    LineageError,
    Nature,
    ProvenanceError,
    Seed,
    SeedError,
    SimultaneityError,
    TickClosedError,
    Valence,
    ValenceError,
)
from alaya.seeds.store import SeedStore

__all__ = [
    "Kind",
    "LineageError",
    "Nature",
    "ProvenanceError",
    "Seed",
    "SeedError",
    "SeedStore",
    "SimultaneityError",
    "Tick",
    "TickClosedError",
    "Valence",
    "ValenceError",
]
