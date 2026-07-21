# Echo — 90-second demo script

**Setup (before you present):**

```bash
cd journal
python3 seed.py --reset      # a month of interconnected entries
export ANTHROPIC_API_KEY=sk-ant-...   # optional but ideal — makes extraction live
python3 app.py               # http://localhost:8777
```

Have the browser open on the **Write** view. If presenting on a phone, the
layout is fully responsive.

---

### 0:00 — The hook (15s)
> "Most journaling apps are a text box and a streak. Echo actually reads what
> you write, and builds a map of your life out of it. Watch."

Point at the **prompt at the top of Write**. Read it aloud — it names a real
person from past entries:
> "See this? It didn't come from a list. Echo noticed I write about Sarah and
> Project Phoenix together, and it's asking me about that."

### 0:15 — Write an entry (25s)
Type something that mentions a **new** person and an **existing** one, e.g.:
> "Lunch with Priya and my sister Maya — Maya's thinking about joining Project Phoenix."

Hit **Save** (or ⌘/Ctrl+Enter). Narrate the moment:
> "It's reading the entry now…" — the button shows *Reading your words…*

When it lands, point at the three things that happen at once:
- the toast — *"1 new name in your world"* (Maya)
- the **reflection** that appears, ending in a question
- (if a streak day) the ember pulse on the ring

### 0:40 — Your world (25s)
Click **Graph**.
> "This is everyone and everything I've written about, connected the way my life
> connects them. Node size is how often something comes up; colors are types —
> people, places, projects."

- **Drag** a node so it's clearly live.
- **Tap the legend** to filter to just people, then back.
- **Click Project Phoenix** → "Open story."

### 1:05 — The payoff: an entity's story (15s)
The story panel opens:
> "Here's Project Phoenix as its own page — who leads it, who works on it, who
> sponsored it, and every entry it appears in. This is the graph paying off:
> my journal became a queryable memory of my life."

Click **"Write about Project Phoenix"** — it drops a prompt into the editor.
> "And it loops right back to writing."

### 1:20 — Close (10s)
Click **Progress** for the streak ring, level, and achievements.
> "Streaks and levels keep me coming back; the graph keeps it personal. It runs
> on Claude for the extraction and reflections, with an offline fallback so it
> always works. That's Echo."

---

## If something goes sideways
- **No API key / network down** → everything still works on fallbacks; entities
  are still extracted (heuristically), the graph still grows. Don't apologize
  for it — it's a feature.
- **Empty graph** → you forgot `seed.py`. Run `python3 seed.py --reset`.
- **Want a clean slate mid-demo** → `python3 seed.py --reset` reseeds instantly.
