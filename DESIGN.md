# Ālaya — Design

**An agent architected as the eight consciousnesses of Yogācāra.**

The doctrinal source is [`docs/yogacara.md`](docs/yogacara.md) (rendered from the artifact
[唯识学纲要](https://claude.ai/code/artifact/dce829ac-8adf-4cf2-919e-ec560cb00b60)). This
document is the mapping from that doctrine to running code.

---

## Why this mapping is not decoration

A 4th-century theory of mind is a strange spec for an agent framework. It earns its place
because it was built to answer three questions that agent engineering is currently bad at,
and it answers them with more precision than the folk models we usually reach for.

| The doctrine's question | The agent-engineering question | What it hands you |
|---|---|---|
| 无心位中，业力凭什么相续？ | What persists across sessions, and with what integrity? | **种子六义** — six checkable storage invariants with total provenance |
| 我们凭什么认为自己认识了外境？ | Which of the agent's beliefs are grounded, and which did it invent? | **三性** — a three-way grounding ontology and the rope-snake test |
| 转依如何可能，各识何时能转？ | What can an agent improve online, and what needs an offline rebuild? | **六七因中转，五八果上圆** — a two-tier improvement schedule |

Everything below follows from those three. Where the mapping is thinner than that, this
document says so rather than dressing it up.

---

## The eight layers

```
     ┌─ 前五识  pañca-vijñāna ────────────────────────┐
     │  alaya/senses/     raw Percept, 现量 only       │  no naming, no judging
     │  eye · ear · body                              │  enforced by type: no label field
     └─────────────────────┬──────────────────────────┘
                           ↓
     ┌─ 第六意识  mano-vijñāna ───────────────────────┐
     │  alaya/mano.py     reactive tool-calling loop   │  the ONLY layer that touches
     │  遍缘一切法 · 分别 · 计度 · 造业最强             │  the world; every act is karma
     └────┬──────────────────────────────────┬────────┘
          │ 种子生现行 (activate)             │ 现行熏种子 (perfume)
          ↓                                  ↓
     ┌─ 第八阿赖耶识  ālaya-vijñāna ──────────────────┐
     │  alaya/seeds/      append-only seed store       │  无覆无记 — never judges,
     │  变现 → 根身 (capabilities)                     │  never deletes, never refuses
     │       → 器世间 (world model)                    │  恒转如瀑流
     │  种子生种子 · 自类相续 (offline consolidation)   │  retrieval IS world-construction
     └─────────────────────┬──────────────────────────┘
                           ↑ reads 见分  ┊  writes bias into every prompt
     ┌─ 第七末那识  manas ────────────────────────────┐
     │  alaya/manas.py    persistent self-model        │  恒审思量 — always on
     │  ⚠ the designated bias source, by construction  │  + audit of its own distortion
     └────────────────────────────────────────────────┘
```

Eight layers, one stream — **八识不是八个心，而是一个心识流的八重功能**. In code that means
they share one store and one tick; they are not eight services.

### 第七识 as a named pathology, not an accident

The doctrine's red line is that manas mistakes the ālaya's 见分 — the *perceiving aspect*,
the activity of knowing — for a permanent knower, and pipes that error into every judgment
the sixth consciousness makes. Read as engineering: **the self-model an agent carries is
structurally a bias source, not a neutral fact.**

So `manas.py` is built with that admission in the type. It reads a projection of the store
(what the agent retrieves, what it attends to, what it keeps calling "I"), writes a
self-description injected into every prompt — and exposes `audit()`, which reports how that
self-description skewed the last *N* decisions. The bias is not a bug to be removed; it is a
load-bearing component that must be measurable. 平等性智 is the metric on it, not its deletion.

---

## 种子熏习 — the causal engine

### The unit

```python
@dataclass(frozen=True)
class Seed:
    id:         str        # content address — sha256 over every field below
    lineage:    str        # 自类相续 — the root id of this seed's self-continuity chain
    tick:       int        # 果俱有 — the tick this seed was perfumed in
    at:         str        # ISO-8601 UTC
    kind:       Kind       # percept | act | claim | reflection | derived
    content:    str
    valence:    Valence    # 性决定 — wholesome | unwholesome | neutral, fixed at write
    nature:     Nature     # 三性 — paratantra | parikalpita | parinispanna
    conditions: tuple[str] # 待众缘 — this seed activates only when all are present
    parents:    tuple[str] # 引自果 — the seeds that conditioned this one
    weight:     float      # strength at the moment of perfuming
```

### 种子六义 as storage invariants

护法's six criteria are not commentary. Each one closes a hole, and each one is a testable
property of the store. `tests/test_six_criteria.py` is the executable form of this table.

| 义 | The doctrine | The invariant in code |
|---|---|---|
| **刹那灭** | 才生即灭，无常住体 | `Seed` is frozen and content-addressed. The store exposes no `update` and no `delete` — mutation is not an operation that exists. |
| **果俱有** | 与所生现行同时俱有 | A seed's `parents` must have been activated or perfumed **in the same tick**. Violating this raises `SimultaneityError`. |
| **恒随转** | 一类相续，至究竟位 | Nothing is ever removed. Strength decays toward a floor above zero; a forgotten seed is a quiet one, not an absent one. |
| **性决定** | 善恶性质不改 | `valence` is fixed at construction and hashed into `id`. Retrieval never touches it; consolidation may only merge seeds of like valence. |
| **待众缘** | 须待缘具方能现行 | `activate(conditions)` fires a seed only when its `conditions` are a subset of the present conditions. Presence in the store is not activation. |
| **引自果** | 各引自类之果 | Every `parents` id must resolve in the store. `trace(id)` walks the full ancestry — every act is attributable to the seeds that produced it. |

### 刹那灭 vs. 恒随转 — the apparent contradiction

A seed must perish every moment *and* persist until countered. This looks like a
specification bug and it is the most interesting part of the design.

The doctrine resolves it with **自类相续**: the seed does not endure and change, it perishes
and re-arises as one of its own kind. Taken literally as an implementation rule:

> `weight` is **not** a mutable field. It is the strength at the instant of perfuming, frozen
> forever. Re-perfuming the same content does not update a row — it appends a **new** seed
> with `parents=(previous,)` and the **same `lineage`**. Present strength is a *computed*
> property of a lineage: decayed originals plus every reinforcement since.

```python
store.strength(lineage, now_tick)   # Σ over the lineage of weight · decay(now − tick)
```

Immutability and decay stop fighting. Reinforcement becomes append-only history rather than a
lost prior value, so "why is this memory strong?" is answerable — you can read the whole
lineage that made it so. This falls directly out of taking 刹那灭 seriously instead of
treating it as a metaphor.

### 三法展转 · 因果同时 — the tick

The three moments are not three steps. They are one transaction:

```python
with store.tick() as t:
    percepts = senses.gather()                       # 现量 — bare intake
    world    = store.manifest(percepts)              # 变现器世间 — world built FROM seeds
    active   = t.activate(world.conditions)          # 种子生现行  (待众缘 applies here)
    bias     = manas.color(world, active)            # 恒审思量
    acts     = mano.run(world, active, bias, tools)  # 造业 — the only outward motion
    t.perfume(percepts, active, acts)                # 现行熏种子 — same transaction
```

The loop has **no first cause and no external ground truth** — 无始以来如是. That is the
doctrine's actual claim, and it is also simply true of an agent whose only world is its own
trace. The world the agent acts on is a *projection from the store*, not raw sensor data:
retrieval is world-construction, and `manifest()` is where that happens.

---

## 三性 — grounding, and the rope-snake gate

Every claim the agent holds carries one of three natures. They are **not three kinds of
thing** — they are three readings of one thing, which is exactly why this works as a tag
rather than a taxonomy.

| Nature | Rope-snake | In the agent |
|---|---|---|
| `paratantra` 依他起 | the rope — 众缘所生 | has a provenance chain to a percept or a tool result |
| `parikalpita` 遍计所执 | the snake — 情有理无 | a model-generated label with no provenance. The hallucination class |
| `parinispanna` 圆成实 | the hemp — 于依他起上远离遍计 | what survives when the fabricated overlay is stripped from the dependent |

**The rope-snake gate** (`examine()`, phase 3) runs before any consequential act: strip every
`parikalpita` layer from the claim, and re-ask whether the act still follows from what
remains. 去掉蛇的是智慧 — and the rope was always just a rope.

Note what the doctrine forbids here, because it is a real constraint on the implementation:
`paratantra` is **similar-but-not-real** (似有非实), not "true". Grounded is not the same as
correct. A gate that promoted provenance to truth would be the naive-realist error the whole
system exists to refuse.

---

## 转识成智 — the improvement schedule

The end state is not the extinction of the layers but **转依**, transformation of the basis.
Each consciousness becomes a wisdom, and — this is the load-bearing part —
**六七因中转，五八果上圆**: they do not all turn at the same time, or at the same cost.

| Transformation | Layer | When | Cost | What it actually does |
|---|---|---|---|---|
| **妙观察智** 因中转 | 6th | online, each cycle | cheap | refine the reactive policy and prompt |
| **平等性智** 因中转 | 7th | online, each cycle | cheap | measure and de-skew the self-model |
| **成所作智** 果上圆 | 前五 | offline batch | expensive | regenerate sensor and tool schemas |
| **大圆镜智** 果上圆 | 8th | offline batch | expensive | full store consolidation and re-embedding |

The reason the doctrine gives is precisely the reason an engineer would give:
分别与我执可先被智慧对治 — discrimination and self-grasping are reachable by reflection
alone, so layers 6 and 7 can be revised live from the agent's own trace. The sense layer and
the store are 果上圆 because they cannot be fixed from inside a running tick; they need the
whole pipeline stopped. Cheap online adaptation of prompt and self-model, expensive offline
rebuild of substrate and sensors — the timing rule *is* the correct engineering split.

The dashed lines in the source artifact — 尚未圆满的转依 — are the progress metric. Each
transformation reports how far along it is; none of them is ever finished.

---

## Where this mapping is thin

Stated plainly, so the rest can be trusted:

- **前五识.** Sensor adapters are sensor adapters. The 现量 discipline — percepts carry no
  labels, only payload, so that all interpretation is attributable to a later layer — is a
  genuinely useful constraint, but it is a small one. Nothing deep is being claimed here.
- **共业 / 器世间.** The doctrine's account of why different people see the same mountain
  (共变, collectively conditioned) is the natural model for multi-agent shared state. Nothing
  in this repo implements it yet. Calling it "designed" would be overreach; it is noted as
  the obvious extension and left in the roadmap.
- **The soteriology.** 转依 in the doctrine is liberation. Here it is a scheduling rule. The
  structural analogy is real and the stakes are not. This project takes the architecture, not
  the salvation.

---

## Repository layout

```
alaya/
├── DESIGN.md                    this document
├── docs/yogacara.md             the doctrinal source text
├── alaya/
│   ├── seeds/                   第八识 — the store
│   │   ├── seed.py              Seed, Kind, Valence, Nature + 六义 validation
│   │   ├── store.py             append-only store, tick transaction, activate/recall/trace
│   │   ├── perfume.py           现行熏种子 — write-back
│   │   ├── manifest.py          变现 — 根身 (capabilities) + 器世间 (world)     [phase 2]
│   │   └── consolidate.py       种子生种子 — offline decay / merge / abstraction [phase 4]
│   ├── senses/                  前五识 — bare percept adapters                  [phase 2]
│   ├── mano.py                  第六识 — reactive tool-calling loop             [phase 2]
│   ├── manas.py                 第七识 — self-model + bias audit                [phase 2]
│   ├── trisvabhava.py           三性 — tagging + rope-snake gate                [phase 3]
│   ├── wisdom/                  转识成智 — the four maturation jobs             [phase 4]
│   └── providers/               claude · openai · base                          [phase 2]
├── mcp_server/server.py         MCP surface for Claude Code                     [phase 5]
├── config/identity.yaml         本愿 — purpose and hard rules
├── data/seeds.jsonl             the store on disk
└── tests/                       六义 invariants, rope-snake, lineage
```

## Phases

| | Phase | Contents | Status |
|---|---|---|---|
| 1 | **Substrate** | `Seed`, store, tick transaction, activate / perfume / recall / trace, 六义 invariant tests | **in progress** |
| 2 | **Loop** | `mano.py`, `manas.py`, senses, `manifest()`, providers, the atomic tick end to end | planned |
| 3 | **Gate** | `trisvabhava.py`, the rope-snake check in the action path | planned |
| 4 | **Turning** | `wisdom/` — online 六七, offline 五八, consolidation | planned |
| 5 | **Surface** | MCP server, CLI, Docker, CI, a runnable reference agent | planned |

Phase order is not arbitrary: nothing above the store works until the store's invariants
hold, which is why phase 1 is tests before code.

---

## Prior art in this codebase

Ālaya is a rebuild of patterns proven in [`vault-whisper/pet`](https://github.com/reachlin/vault-whisper)
(the AI pet, Pepper), which already had three of the eight layers in embryo:

| Pepper | Ālaya |
|---|---|
| `brain/loop.py` — fast reactive tool-calling tick | 第六意识 `mano.py` |
| `brain/overseer.py` — slow reflective loop rewriting `directive.md` | 第七末那识 `manas.py` |
| `brain/longterm_memory.py` — append-only markdown, newest first, never deleted | 第八阿赖耶识 `seeds/` |

What Pepper lacks, and what the doctrine supplies: provenance, seed-level invariants, belief
grounding, and a principled account of what may be improved when.
