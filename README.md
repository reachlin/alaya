# Ālaya · 阿賴耶

**A memory-native AI agent, architected as the eight consciousnesses of Yogācāra.**

Most agents bolt memory onto a loop. Ālaya inverts it: the agent **is** its store, and the
loops are what the store does when conditions meet it. That inversion is not an aesthetic
choice — it comes from a 4th-century theory of mind built to answer exactly the questions
agent engineering is currently worst at.

```
前五識  alaya/senses/    bare signals — camera, microphone, and three faculties awaiting devices
第六識  alaya/mano.py    the reactive loop — the only layer that touches the world
第七識  alaya/manas.py   the self-model — always on, and the designated bias source
第八識  alaya/seeds/     the store — append-only, morally neutral, never deletes
```

Four things the doctrine hands you that a folk model of memory does not:

- **種子六義 → six storage invariants.** Immutable content-addressed seeds, cause and fruit
  in one transaction, decay-never-delete, valence fixed at write, conditional activation,
  and categories that do not cross. They are unit tests, not commentary.
- **三量 → the measure is computed, never claimed.** Every claim is recorded as 現量 (direct),
  比量 (inferred), or 非量 (erroneous) — and an agent cannot rate its own certainty, so the
  measure is derived from what actually arose. A model may *downgrade* to doubt; it can never
  upgrade, and 現量 is not available to it at all. 前五識唯現量: naming is not perceiving.
- **三性 → the rope-snake gate.** Before an act, separate what actually arose (the rope) from
  what the claim laid over it (the snake), and say what remains once the snake is removed.
  三性 is an ontology and 三量 an epistemology; conflating them is the most common way this
  material gets misapplied, including by an earlier draft of this repo.
- **六七因中轉，五八果上圓 → an improvement schedule that is enforced, not described.** The
  prompt and self-model are revised live from the agent's own trace; the sensors and the store
  need the stream stopped. A 果上圓 turning attempted mid-tick raises.

Read **[DESIGN.md](DESIGN.md)** for the full mapping and **[docs/yogacara.md](docs/yogacara.md)**
for the doctrinal source ([唯識學綱要](https://claude.ai/code/artifact/dce829ac-8adf-4cf2-919e-ec560cb00b60)).
The code is written to be read: every module opens with what the doctrine says, and every
rule carries the reason it takes the shape it does.

---

## Status

| Phase | Contents | |
|---|---|---|
| 1 · Substrate | `Seed`, store, tick transaction, activate / perfume / recall / trace | **shipped** |
| 2 · Loop | senses, `manifest()`, `mano`, `manas`, providers, console, MCP | **shipped** |
| 3 · Gate | 绳蛇检验 — the rope-snake check in the action path | **shipped** |
| 4 · Turning | 轉識成智 — online 六七, offline 五八, consolidation | **shipped** |
| 5 · Surface | Docker, a runnable reference agent, 共業 across agents | planned |

**267 tests**, tests-first throughout.

---

## Quick start

```bash
git clone https://github.com/reachlin/alaya.git && cd alaya
pip install -r requirements.txt          # core only
pip install -e ".[all]"                  # + camera, microphone, model providers, MCP
pytest

python -m alaya                          # offline — no API key needed
```

The console opens and does nothing until you tell it to. Press Enter to live one 刹那.

```
› you smell pizza

── 刹那 1 ─────────────────────────
  ◦ [nose·injected] pizza
  → speak my nose has something: pizza
  → remember nose: pizza [anumana]

› you hear a dog barking

── 刹那 2 ─────────────────────────
  ◦ [ear·injected] a dog barking
  ↑ 種子生現行 nose: pizza (4fc9c7eb)
  → speak my ear has something: a dog barking
```

The second moment shows the machine working: nothing asked for the pizza memory. It arose
because the conditions it was perfumed under were met again — 種子生現行, retrieval as a
consequence of the present rather than a query against the past.

| Input | What happens |
|---|---|
| `<enter>` | live one moment |
| `you smell pizza` | a percept enters 鼻識 (also: see / hear / smell / taste / feel) |
| `/smell pizza` | the same, short form |
| anything else | spoken aloud — the agent hears it through its ear, as speech should arrive |
| `/trace <id>` | the full ancestry of any seed, back to the percepts |
| `/manas` `/audit` | the self-model, and how much it has been bending conduct |
| `/world` `/status` `/recall` `/senses` `/auto [secs]` `/help` | |

With a real sixth consciousness:

```bash
python -m alaya --provider claude        # ANTHROPIC_API_KEY
python -m alaya --provider openai        # OPENAI_API_KEY
python -m alaya --say --listen           # speak aloud; transcribe the microphone
```

---

## 绳蛇检验 — the rope-snake gate

《攝大乘論》: in dim light you see a coiled rope and recoil from a snake. The claim is the
snake; what actually arose is the rope; and the third nature is not a fourth thing behind
the rope but the rope seen without the snake on it. 去掉蛇的是智慧 — 而繩始終是那條繩.

```
› /examine pizza left by my neighbour

claim: pizza left by my neighbour
verdict: overlaid (33% of it arose)
遍計所執 (added by you, borne by nothing): left, neighbour
依他起 (what actually arose): pizza
without the addition, you have: pizza
```

The gate runs on every claim and every outward act. It sets the seed's 三性 — a claim that
exceeds its basis is recorded 遍計所執 — while 三量 stays on provenance, because a lexical
examiner must never be able to demote a genuine inference to 非量. Two axes, two questions.

**Expect most claims to come back overlaid.** That is not the gate malfunctioning. 遍計所執 is
the *ordinary* condition of unawakened cognition — the doctrine's claim is that superimposition
is what ordinary knowing consists of, not an occasional lapse. A gate reporting clean most of
the time would be the broken one. The signal is not "is there a snake" but "how much of this
act rests on it".

By default the gate **marks rather than blocks** — 無覆無記 carried up from the store, which
never refuses what it is given. `--strict` refuses outward acts resting on nothing, and hands
back the residue so the model can say the true smaller thing instead:

```bash
python -m alaya --strict
```

`TermExaminer` is the default: literal, deterministic, and deliberately blunt. It cannot see
that "dark" follows from "luminance 0.02" and will over-report fabrication — the safe
direction for a gate, since an examiner that guesses generously about what its grounds imply
is one that launders fabrication. `ModelExaminer` judges implication instead, and falls back
to the literal one on any failure so the gate fails closed rather than open.

---

## 轉識成智 — the turning

Each consciousness becomes a wisdom. Not by being extinguished — 轉依 is a transformation of
the *basis*, the same faculties no longer organised around 自我.

```
› /wisdom

轉識成智 — all four
  前五識      → 成所作智  ████████████ 100%  [果上圓]
  第六意識     → 妙觀察智  ████████████ 100%  [因中轉]
  第七末那識    → 平等性智  ████████┄┄┄┄  70%  [因中轉]
  第八阿賴耶識   → 大圓鏡智  ████████┄┄┄┄  67%  [果上圓]
      2 thing(s) said 4 times — the largest 2×: nose, pizza
  ──────────────────────────────────────────
  轉依 overall 84% — 尚未圓滿
```

The dashed lines are the point. No transformation is ever reported finished.

**六七因中轉，五八果上圓** — they do not all turn together, and that timing rule is the most
useful thing the doctrine says about self-improvement:

| | Layer | When | What it does |
|---|---|---|---|
| **妙觀察智** | 6th | `/turn` — online, cheap | reads the gate's own verdicts and writes the standing directive the sixth consciousness reads next moment |
| **平等性智** | 7th | `/turn` — online, cheap | measures how partial the self-model has become and appends a correction, leaving the account standing |
| **成所作智** | 前五 | `/turn fruit` — offline | attribution per faculty; recalibrates the ear's threshold, reports the rest |
| **大圓鏡智** | 8th | `/turn fruit` — offline | 種子生種子 — consolidates redundant arisings |

The doctrine's reason is the engineer's reason: 分別 and 我執 are reachable by wisdom directly,
so they can be revised while practice continues. The senses and the store cannot be corrected
from inside their own operation. `/turn fruit` mid-tick raises `UntimelyError`.

### Consolidation cannot be garbage collection

The obvious way to handle fifty near-identical memories is to merge them and drop the rest.
Both halves are forbidden here — 剎那滅 makes seeds unrewritable, 恆隨轉 unremovable. So
consolidation is **additive**: a new abstraction is laid down carrying the *intersection* of
its members' conditions, so it fires wherever any member would. Retrieval surfaces one thing
instead of fifty, and nothing was lost.

Then 果俱有 forces the elegant part. To cite the fifty as parents they must be *present*, so
the consolidator opens a tick and activates them first: **you cannot abstract from memories you
have not actually recalled.** Nobody designed that in — it falls out of the second criterion.

---

## The senses

眼識 and 耳識 have devices. 鼻識, 舌識 and 身識 do not — which is not an error but 無心位
for those faculties, and they accept injection like any other.

The discipline the whole layer is built on is **唯現量**: the five senses present, they do not
name. The eye reports `frame 1280×720 · luminance 0.42 · motion 0.11` — properties of the
light. It never reports "a person at a desk", because that is a *name*, and naming is the
sixth consciousness's work, recorded as its inference and defeasible as such. Draw that line
anywhere later and the information about who did the naming is already gone.

**macOS permissions.** The first camera or microphone access needs Privacy & Security →
Camera / Microphone → your terminal app, then a restart of the terminal. Without it the
faculty reports itself unavailable and the stream continues — a shut eye, not a crash.

### Adding a sensor over Bluetooth

No new faculty type is needed. Every faculty carries a thread-safe inbox, so a push feed —
BLE notify, MQTT, serial, websocket — just calls `inject()` from its own thread and the next
tick drains it:

```python
field = SenseField()
threading.Thread(target=lambda: ble_notify(
    lambda reading: field.inject(Sense.BODY, reading, source=Source.SENSED)
)).start()
```

Pass `Source.SENSED` for real hardware; the console's default `INJECTED` marks percepts a
human typed. The agent cannot tell the difference from the inside — nothing can, that is what
it is for a percept to arise — but `trace()` shows anyone afterwards exactly which conclusions
rest on things a person made up. For a pull-based device, subclass `Faculty` and implement
`available` and `sense_now`; that is the whole interface.

---

## MCP — one server, not five

`mcp_server/server.py` exposes the stream to Claude Code: `alaya_see`, `alaya_hear`,
`alaya_smell`, `alaya_taste`, `alaya_touch`, `alaya_moment`, `alaya_recall`, `alaya_trace`,
`alaya_manas`, `alaya_status`.

A server per sense is the obvious design and the wrong one. Devices are exclusive, so five
processes would contend for one camera. The tick is a transaction, so splitting it across
processes buys a distributed commit in exchange for nothing. And 八識不是八個心 — the eight
are functions of one stream, not eight minds in a committee. Sharding the senses into
separate processes would encode the exact error the source text spends its first chapter
refuting.

---

## What the store will not do

`SeedStore` has no `update()` and no `delete()`. Not discouraged — the methods do not exist.
刹那滅 makes seeds immutable; 恆隨轉 makes them undeletable; a forgotten memory is a quiet
one, not an absent one. The store is 無覆無記 — morally neutral: it never judges what it is
given and never refuses it. Recording a claim as 非量 is a tag, not a veto.

Reinforcement is therefore an append, never a mutation. Re-perfuming a memory adds a new
arising on the same lineage — 自類相續, the seed perishing and re-arising as one of its own
kind — so "why is this memory strong?" is always answerable by reading the chain.

---

## Prior art

Ālaya rebuilds patterns proven in [vault-whisper/pet](https://github.com/reachlin/vault-whisper)
(Pepper, the AI pet), which already had three of the eight layers in embryo: a fast reactive
tool loop, a slow reflective overseer, and an append-only markdown memory. What it lacked was
provenance, invariants, belief grounding, and a principled account of what may be improved
when.

There is academic work relating Yogācāra to AI — Kim's [*A Buddhist Yogācāra Perspective on
the Singularity*](https://philarchive.org/archive/KIMABY), and [*Between No-Self and the
Algorithm*](https://www.mdpi.com/2077-1444/17/3/378) in *Religions* — but as far as a search
turns up, no agent framework has implemented the eight consciousnesses as running code.

## License

MIT
