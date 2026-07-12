# Echo — AI journaling with a knowledge graph of your life

Echo helps you **process and document the events of your life**, keeps you
**consistent** with streaks, XP, levels, and achievements, and builds a
**knowledge graph** of the people, places, and projects you write about — then
uses that graph to suggest what to write about next.

## Run it

```bash
cd journal
python3 app.py
# open http://localhost:8777
```

Zero required dependencies — Python 3.9+ stdlib and SQLite only.

### Enable Claude (recommended)

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...
python3 app.py
```

With a key set, Claude (`claude-opus-4-8`) powers:

- **Entity & relationship extraction** — every entry is parsed for the people,
  places, organizations, projects, activities, and events in your life, plus
  labeled relationships between them ("works with", "argued with", "part of").
- **Reflections** — after each entry you get a short, warm reflection with a
  follow-up question, to help you process what you wrote.
- **Personalized prompts** — generated from your knowledge graph, referencing
  your actual world by name.

Without a key, deterministic fallbacks keep every feature working (heuristic
entity extraction, co-occurrence edges, template reflections and graph-rule
prompts) — just with less nuance.

## How it works

| Piece | What it does |
|---|---|
| `app.py` | stdlib HTTP server + JSON API, serves the single-page frontend |
| `db.py` | SQLite schema: entries, entities, mentions, edges, achievements, prompts |
| `ai.py` | Claude integration (structured-output extraction, reflections, prompt generation) + offline fallbacks |
| `graph.py` | knowledge-graph persistence and **edge-driven prompt rules** |
| `gamification.py` | streaks, XP, levels, achievement unlocks, 14-day history |
| `static/index.html` | the app: write view, journal, force-directed graph canvas, progress dashboard |

### Edge-driven suggestions

The graph doesn't just visualize — it drives prompts:

- **Dormant nodes**: "You haven't written about Sarah in 12 days — how are
  things between you two?"
- **Strong edges**: "Sarah and Project Phoenix keep showing up together — what
  does that connection mean to you right now?"
- **New nodes**: "You mentioned Marcus for the first time — tell the story of
  how they came into the picture."
- **AI prompts**: Claude reads a summary of the whole graph and writes prompts
  that only make sense for *your* life.

### Gamification

- 🔥 **Streaks** — consecutive days journaled (today or yesterday keeps it alive)
- **XP & levels** — 10 XP per entry, +1 per 50 words, +5 per new entity, across
  11 levels from *New Page* to *Legend*
- 🏆 **11 achievements** — first entry, streak milestones, word counts, and
  graph milestones (10/50 entities, 10/50 relationships)

## API

| Route | Method | Purpose |
|---|---|---|
| `/api/entries` | GET/POST | list entries / create (runs extraction + gamification) |
| `/api/entries/{id}` | GET/DELETE | full entry with entities / delete |
| `/api/graph` | GET | `{nodes, links}` for the force layout |
| `/api/stats` | GET | streaks, level, totals, achievements, 14-day history |
| `/api/prompts` | GET | refresh + list active prompts |
| `/api/prompts/{id}/dismiss` | POST | hide a prompt |

Data lives in `journal/journal.db` (override with `JOURNAL_DB`); port defaults
to 8777 (override with `JOURNAL_PORT`).
