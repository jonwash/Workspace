"""Gamification: streaks, XP, levels, and achievements — all derived from the data."""

from datetime import date, timedelta

# XP awards
XP_PER_ENTRY = 10
XP_PER_50_WORDS = 1          # capped below
XP_WORDS_CAP = 20            # max word-XP per entry (1000 words)
XP_PER_NEW_ENTITY = 5

LEVELS = [0, 30, 80, 160, 280, 450, 700, 1050, 1500, 2100, 2900]
LEVEL_NAMES = [
    "New page", "Notetaker", "Scribe", "Chronicler", "Storyteller",
    "Memoirist", "Historian", "Sage", "Archivist", "Loremaster", "Legend",
]

# (icon, name, condition) — icons are Lucide glyph names from the design system
ACHIEVEMENTS = {
    "first_entry":   ("sprout",    "First words", "Write your first entry"),
    "entries_5":     ("book-open", "Getting into it", "Write 5 entries"),
    "entries_25":    ("calendar",  "Shelf space", "Write 25 entries"),
    "streak_3":      ("leaf",      "Taking root", "A 3-day streak"),
    "streak_7":      ("sun",       "One week", "A 7-day streak"),
    "streak_30":     ("moon",      "A full moon", "A 30-day streak"),
    "wordsmith":     ("feather",   "Wordsmith", "Write a 500-word entry"),
    "cast_10":       ("user",      "Ensemble cast", "10 names in your world"),
    "cast_50":       ("map-pin",   "Whole world", "50 names in your world"),
    "connector_10":  ("share-2",   "Connector", "10 relationships mapped"),
    "connector_50":  ("activity",  "Mind mapper", "50 relationships mapped"),
}


def _entry_dates(conn):
    return [r["entry_date"] for r in conn.execute(
        "SELECT DISTINCT entry_date FROM entries ORDER BY entry_date DESC")]


def compute_streak(conn):
    """Current and longest streak of consecutive days with entries."""
    dates = [date.fromisoformat(d) for d in _entry_dates(conn)]
    if not dates:
        return 0, 0

    # Current streak: counts if the latest entry is today or yesterday.
    today = date.today()
    current = 0
    if dates[0] >= today - timedelta(days=1):
        current = 1
        for prev, nxt in zip(dates, dates[1:]):
            if prev - nxt == timedelta(days=1):
                current += 1
            else:
                break

    longest = run = 1
    ordered = sorted(dates)
    for a, b in zip(ordered, ordered[1:]):
        run = run + 1 if b - a == timedelta(days=1) else 1
        longest = max(longest, run)
    return current, max(longest, current)


def compute_xp(conn):
    row = conn.execute("SELECT COUNT(*) n, COALESCE(SUM(word_count), 0) w FROM entries").fetchone()
    entities = conn.execute("SELECT COUNT(*) c FROM entities").fetchone()["c"]
    word_xp = min(row["w"] // 50 * XP_PER_50_WORDS, row["n"] * XP_WORDS_CAP)
    return row["n"] * XP_PER_ENTRY + word_xp + entities * XP_PER_NEW_ENTITY


def level_for_xp(xp):
    level = 0
    for i, threshold in enumerate(LEVELS):
        if xp >= threshold:
            level = i
    nxt = LEVELS[level + 1] if level + 1 < len(LEVELS) else None
    return {
        "level": level + 1,
        "name": LEVEL_NAMES[level],
        "xp": xp,
        "next_level_xp": nxt,
        "progress": 1.0 if nxt is None else round((xp - LEVELS[level]) / (nxt - LEVELS[level]), 3),
    }


def check_achievements(conn):
    """Unlock any newly-earned achievements; returns list of newly unlocked keys."""
    entries = conn.execute("SELECT COUNT(*) c FROM entries").fetchone()["c"]
    entities = conn.execute("SELECT COUNT(*) c FROM entities").fetchone()["c"]
    edges = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]
    max_words = conn.execute("SELECT COALESCE(MAX(word_count), 0) m FROM entries").fetchone()["m"]
    current, longest = compute_streak(conn)

    earned = set()
    if entries >= 1: earned.add("first_entry")
    if entries >= 5: earned.add("entries_5")
    if entries >= 25: earned.add("entries_25")
    if longest >= 3: earned.add("streak_3")
    if longest >= 7: earned.add("streak_7")
    if longest >= 30: earned.add("streak_30")
    if max_words >= 500: earned.add("wordsmith")
    if entities >= 10: earned.add("cast_10")
    if entities >= 50: earned.add("cast_50")
    if edges >= 10: earned.add("connector_10")
    if edges >= 50: earned.add("connector_50")

    have = {r["key"] for r in conn.execute("SELECT key FROM achievements")}
    new = earned - have
    for key in new:
        conn.execute("INSERT OR IGNORE INTO achievements (key) VALUES (?)", (key,))
    conn.commit()
    return sorted(new)


def stats(conn):
    current, longest = compute_streak(conn)
    xp = compute_xp(conn)
    entries = conn.execute("SELECT COUNT(*) c FROM entries").fetchone()["c"]
    entities = conn.execute("SELECT COUNT(*) c FROM entities").fetchone()["c"]
    edges = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]
    words = conn.execute("SELECT COALESCE(SUM(word_count), 0) w FROM entries").fetchone()["w"]

    unlocked = {r["key"]: r["unlocked_at"] for r in conn.execute("SELECT * FROM achievements")}
    achievements = [
        {"key": k, "icon": i, "name": n, "description": d,
         "unlocked": k in unlocked, "unlocked_at": unlocked.get(k)}
        for k, (i, n, d) in ACHIEVEMENTS.items()
    ]

    # Last 14 days of activity for the consistency chart.
    today = date.today()
    counts = {r["entry_date"]: r["c"] for r in conn.execute("""
        SELECT entry_date, COUNT(*) c FROM entries
        WHERE entry_date >= date('now', '-13 days') GROUP BY entry_date""")}
    history = [
        {"date": (today - timedelta(days=i)).isoformat(),
         "count": counts.get((today - timedelta(days=i)).isoformat(), 0)}
        for i in range(13, -1, -1)
    ]

    return {
        "streak": {"current": current, "longest": longest},
        "level": level_for_xp(xp),
        "totals": {"entries": entries, "entities": entities,
                   "relationships": edges, "words": words},
        "achievements": achievements,
        "history": history,
    }
