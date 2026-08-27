# Ālaya · 阿赖耶

**A memory-native AI agent, architected as the eight consciousnesses of Yogācāra.**

Most agents bolt memory onto a loop. Ālaya inverts it: the agent **is** its store, and the
loops are what the store does when conditions meet it. That inversion is not an aesthetic
choice — it comes from a 4th-century theory of mind that was built to answer exactly the
questions agent engineering is currently worst at.

```
前五识  senses/        bare percepts — no naming, no judging
第六识  mano.py        the reactive loop — the only layer that touches the world
第七识  manas.py       the self-model — always on, and the designated bias source
第八识  seeds/         the store — append-only, neutral, never deletes
```

Three things the doctrine hands you that a folk model of memory does not:

- **种子六义 → six storage invariants.** Immutable content-addressed seeds, simultaneous
  cause and fruit, decay-never-delete, valence fixed at write, conditional activation, and
  total provenance. Every action traces back to the seeds that produced it. They are unit
  tests, not commentary.
- **三性 → a grounding ontology.** Every claim is tagged *dependently-arisen* (has
  provenance), *fabricated* (model-invented — the hallucination class), or *perfected* (what
  survives when the fabrication is stripped). The rope-snake gate runs before any
  consequential act.
- **六七因中转，五八果上圆 → an improvement schedule.** The prompt and the self-model can be
  revised live from the agent's own trace; the sensors and the store need an offline rebuild.
  The doctrine's timing rule is the correct engineering split.

Read **[DESIGN.md](DESIGN.md)** for the full mapping, and **[docs/yogacara.md](docs/yogacara.md)**
for the doctrinal source ([唯识学纲要](https://claude.ai/code/artifact/dce829ac-8adf-4cf2-919e-ec560cb00b60)).

---

## Status

**Phase 1 — the substrate — is shipped.** The seed store and its six invariants, written
tests-first: **67 tests**, of which 30 are the executable form of 種子六義. Nothing above the
store works until the store is right, so the store is the whole of phase 1.

```
alaya/seeds/
├── seed.py      Seed · Kind · Valence · Nature — frozen, content-addressed
├── perfume.py   Tick — 三法展转，因果同时: activate and perfume in one transaction
└── store.py     SeedStore — append-only, activate / recall / strength / trace
```

| Phase | Contents | Status |
|---|---|---|
| 1 · Substrate | `Seed`, store, tick transaction, activate / perfume / recall / trace | **shipped** |
| 2 · Loop | `mano.py`, `manas.py`, senses, `manifest()`, providers | planned |
| 3 · Gate | 三性 tagging, the rope-snake check | planned |
| 4 · Turning | 转识成智 — online 六七, offline 五八 | planned |
| 5 · Surface | MCP server, CLI, Docker, reference agent | planned |

---

## Quick start

```bash
git clone https://github.com/reachlin/alaya.git
cd alaya
pip install -r requirements.txt
pytest
```

### The tick — 三法展转，因果同时

Cause, effect, and re-perfuming are one transaction, not three steps:

```python
from alaya.seeds import SeedStore, Kind, Valence, Nature

store = SeedStore("data/seeds.jsonl")

with store.tick() as t:
    # 种子生现行 — a seed fires only when its conditions are met (待众缘)
    active = t.activate(conditions={"topic:weather", "user:lin"})

    # 现行熏种子 — write back, in the SAME tick (果俱有)
    t.perfume(
        content="user asked about the forecast and seemed hurried",
        kind=Kind.PERCEPT,
        valence=Valence.NEUTRAL,
        nature=Nature.PARATANTRA,          # grounded — it came from a percept
        conditions={"topic:weather", "user:lin"},
        parents=[s.id for s in active],    # 引自果 — provenance is mandatory
    )
```

### Reinforcement is history, not mutation

Re-perfuming the same memory never overwrites a row. It appends a new seed on the same
lineage — 自类相续, the seed perishing and re-arising as one of its own kind. Present
strength is *computed* from the whole chain, so "why is this memory strong?" is always
answerable.

```python
strength = store.strength(lineage_id, now_tick)   # Σ weight · decay(now − tick)
ancestry = store.trace(seed_id)                   # 引自果 — the full karmic chain
```

### What the store will not do

`SeedStore` has no `update()` and no `delete()`. Not "discouraged" — the methods do not
exist. 刹那灭 makes seeds immutable; 恒随转 makes them undeletable; a forgotten memory is a
quiet one, not an absent one. The store is 无覆无记 — morally neutral, it never judges what
it is given, and it never refuses.

---

## Prior art

Ālaya rebuilds patterns proven in [vault-whisper/pet](https://github.com/reachlin/vault-whisper)
(Pepper, the AI pet), which already had three of the eight layers in embryo: a fast reactive
tool loop, a slow reflective overseer, and an append-only markdown memory. What it lacked was
provenance, invariants, belief grounding, and a principled account of what may be improved
when. That is what the doctrine supplies.

## License

MIT
