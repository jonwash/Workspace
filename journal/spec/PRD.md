# Echo — Product Requirements (narrative layer)

> **Two-file baseline.** This is the human-readable half of Echo's product spec:
> problem, personas, flows, and rationale. Its machine-actionable counterpart is
> [`product_spec.yaml`](product_spec.yaml), which an agent validates and executes
> against. Where the two overlap, `product_spec.yaml` is authoritative for
> acceptance criteria and evaluation; this document is authoritative for intent
> and rationale.

---

## 1. Problem & purpose

People want to process and remember their lives, but journaling apps stop at a
text box and a streak counter. The writing goes in and nothing comes back out —
no synthesis, no memory, no reason to return tomorrow beyond guilt.

**Echo reads what you write.** Every entry is parsed for the people, places, and
projects in your life and the relationships between them, building a knowledge
graph — *your world* — that you can explore. That graph then generates your next
prompts, so the app grows more personal the more you use it. The result is a
journal that helps you **process** (a reflection after each entry), stay
**consistent** (warm, organic gamification), and accumulate a **queryable memory**
of your own life.

**One-line intent:** *A private journal that turns your entries into a living map
of your life and uses that map to know what to ask you next.*

## 2. Non-goals

- Not a social product — no accounts, sharing, following, or multi-user data.
- Not a note-taking or task manager — entries are reflective, not actionable to-dos.
- Not a search engine — browsing is by entry, entity, and graph, not full-text query (yet).
- Not a cloud service in its current form — single-user, local-first, one SQLite file.
- The AI never fabricates entries or edits the user's words; it only extracts,
  reflects, and prompts.

## 3. Personas

| Persona | Need | What Echo gives them |
|---|---|---|
| **The reflective writer** (primary) | A nightly ritual that helps them make sense of the day | Low-friction editor + a warm reflection with one follow-up question |
| **The lapsed journaler** | A reason to come back after breaking the habit | Streaks, levels, achievements — encouraging, never guilt-tripping |
| **The life cartographer** | To see the shape of their relationships and projects over time | The interactive knowledge graph and per-entity "stories" |

## 4. The core loop

```
write an entry → Claude extracts entities + relationships → your world (graph) grows
      ↑                                                              │
      └──────── the graph's edges generate your next prompts ◄───────┘
```

Three reinforcing pillars:

1. **Processing** — after saving, a 2–3 sentence second-person reflection ending
   in a question. The emotional payoff that makes saving feel worthwhile.
2. **Consistency** — streaks (kept alive by writing today or yesterday), XP,
   eleven named levels, and eleven achievements. Tone is quiet and organic
   ("A full moon — a 30-day streak"), never corporate.
3. **Knowledge graph** — the signature feature and the prompt engine. Entities
   are typed (person / place / organization / project / activity / event /
   other); edges carry a label and a weight (how often two things co-occur).

## 5. UX flows (summary)

Full state/transition/oracle detail is in `product_spec.yaml` under `ux.flows`.

- **F1 — Write & reflect.** Compose an entry (optional title, mood 1–5, backdate)
  → save → see extraction result (new entities), any achievement unlocks, and the
  reflection. The prompt list refreshes from the updated graph.
- **F2 — Explore your world.** Open Graph → drag nodes, hover/tap for a node's
  connections, filter by entity type via the legend, open a node's story.
- **F3 — An entity's story.** Click any entity chip (on an entry) or graph node →
  a panel showing its type, mention count, connections with labels, and every
  entry that mentions it, plus a "write about this" shortcut back into F1.
- **F4 — Look back.** Journal view lists entries reverse-chronologically; open one
  for full text, its reflection, entity chips, and a two-tap delete.
- **F5 — Progress.** Streak ring, level + XP, 14-day activity chart, achievements.

## 6. Success metrics

**Product outcomes (what "working" looks like for a user):**

| Metric | Definition | Why it matters |
|---|---|---|
| Return rate | % of users who write on ≥2 distinct days | The habit is the product |
| Median streak length | Consecutive-day streak across active users | Consistency is a core pillar |
| Entries per active week | Volume of reflection | Engagement depth |
| Graph richness | Entities + relationships per active user | The graph is the moat; richer = stickier |
| Prompt acceptance | % of shown prompts inserted into an entry | Whether graph-driven prompts actually resonate |

**Engineering & product-quality outcomes (pre-merge):** the acceptance criteria
and evaluation protocol in `product_spec.yaml` all pass; the app runs with zero
required dependencies; every AI call has a working offline fallback.

## 7. Constraints & assumptions (Spec Parameters)

These are the parameters the research methodology insists on surfacing. Echo's
values are concrete rather than `<unspecified>`:

- **Language/stack:** Python 3.9+ standard library + SQLite; single-page frontend
  (vanilla HTML/CSS/JS, no build step). No runtime dependencies.
- **Scale:** single user, single process, one SQLite file; hundreds of entries,
  tens-to-hundreds of entities. Not multi-tenant.
- **Deployment:** local-first (localhost); optionally a single hosted instance.
  No horizontal scaling assumed.
- **AI dependency:** Claude (`claude-opus-4-8`) via the Anthropic SDK when
  `ANTHROPIC_API_KEY` is set; deterministic fallbacks otherwise. The app must be
  fully functional offline.
- **Autonomy (for agents working on this repo):** semi-autonomous — an agent may
  modify code, run the evaluation protocol, and open a PR, but must not merge,
  deploy, or add runtime dependencies without human approval. See
  [`../../AGENTS.md`](../../AGENTS.md).

## 8. Privacy posture

A journal is among the most sensitive data a person keeps. Echo is local-first
by default: entries live in one SQLite file on the user's machine and are never
sent anywhere except, when a key is configured, to the Anthropic API for
extraction/reflection/prompt generation. There are no analytics, no third-party
trackers, and no telemetry in the shipped app. Any future hosted or instrumented
version must treat entry content as sensitive by default (see the telemetry and
privacy fields in `product_spec.yaml`).
