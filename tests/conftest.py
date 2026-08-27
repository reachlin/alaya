import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from alaya.seeds import Kind, Nature, SeedStore, Valence


@pytest.fixture
def store(tmp_path):
    return SeedStore(tmp_path / "seeds.jsonl")


def percept(tick, content, conditions=(), **kw):
    """Perfume a root percept — no parents, so it needs no prior activation."""
    return tick.perfume(
        content=content,
        kind=kw.pop("kind", Kind.PERCEPT),
        valence=kw.pop("valence", Valence.NEUTRAL),
        nature=kw.pop("nature", Nature.PARATANTRA),
        conditions=conditions,
        **kw,
    )
