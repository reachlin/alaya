"""第八阿赖耶识 — the seed store and its six criteria.

種子六義, as invariants rather than commentary:

    剎那滅  seeds are frozen and content-addressed; there is no update, no delete
    果俱有  a seed's parents must be *present* in the tick that bore it, not
            merely on file — which is also what makes ``trace`` total
    恆隨轉  nothing is removed; a lineage succeeds itself like a waterfall
    性決定  valence is fixed at write; derived seeds keep their parents' valence
    待眾緣  a seed fires only when all of its conditions are present
    引自果  色心不相互生 — categories do not cross: a lineage continues as its
            own kind, and a derived seed is not drawn from a mixture

Seeds also carry 三量 (:class:`Pramana`), the epistemic axis, which is
orthogonal to 三性 (:class:`Nature`), the ontological one.
"""
from alaya.seeds.perfume import Tick
from alaya.seeds.seed import (
    Kind,
    KindError,
    LineageError,
    Nature,
    Pramana,
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
    "KindError",
    "LineageError",
    "Nature",
    "Pramana",
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
