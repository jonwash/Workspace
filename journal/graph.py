"""Knowledge graph: entity/edge persistence and edge-driven prompt suggestions."""

import hashlib
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def upsert_extraction(conn, entry_id, extraction):
    """Persist extracted entities/relationships for an entry. Returns #new entities."""
    new_entities = 0
    ids = {}

    for ent in extraction.get("entities", []):
        name = ent.get("name", "").strip()
        if not name:
            continue
        etype = ent.get("type", "other")
        row = conn.execute("SELECT id, type FROM entities WHERE name = ?", (name,)).fetchone()
        if row:
            eid = row["id"]
            # Let a typed extraction upgrade an untyped fallback guess.
            newtype = etype if row["type"] == "other" and etype != "other" else row["type"]
            conn.execute(
                "UPDATE entities SET mention_count = mention_count + 1, last_seen = ?, type = ? WHERE id = ?",
                (_now(), newtype, eid))
        else:
            cur = conn.execute(
                "INSERT INTO entities (name, type, mention_count) VALUES (?, ?, 1)",
                (name, etype))
            eid = cur.lastrowid
            new_entities += 1
        ids[name.lower()] = eid
        conn.execute(
            "INSERT OR IGNORE INTO entity_mentions (entry_id, entity_id) VALUES (?, ?)",
            (entry_id, eid))

    for rel in extraction.get("relationships", []):
        sid = ids.get(rel.get("source", "").lower())
        tid = ids.get(rel.get("target", "").lower())
        label = (rel.get("label") or "appears with").strip().lower()
        if not sid or not tid or sid == tid:
            continue
        # Keep edges undirected-ish: store with the smaller id first.
        if sid > tid:
            sid, tid = tid, sid
        conn.execute("""
            INSERT INTO edges (source_id, target_id, label, weight, last_seen)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT (source_id, target_id, label)
            DO UPDATE SET weight = weight + 1, last_seen = excluded.last_seen
        """, (sid, tid, label, _now()))

    conn.commit()
    return new_entities


def get_graph(conn):
    """Full graph as {nodes, links} for the frontend force layout."""
    nodes = [dict(r) for r in conn.execute(
        "SELECT id, name, type, mention_count, first_seen, last_seen FROM entities")]
    links = [dict(r) for r in conn.execute("""
        SELECT e.source_id AS source, e.target_id AS target, e.label, e.weight, e.last_seen
        FROM edges e""")]
    return {"nodes": nodes, "links": links}


def summary_for_ai(conn, limit=40):
    """Compact graph summary fed to Claude for prompt generation."""
    entities = [dict(r) for r in conn.execute("""
        SELECT name, type, mention_count, date(last_seen) AS last_seen
        FROM entities ORDER BY mention_count DESC LIMIT ?""", (limit,))]
    edges = [dict(r) for r in conn.execute("""
        SELECT s.name AS source, t.name AS target, e.label, e.weight
        FROM edges e
        JOIN entities s ON s.id = e.source_id
        JOIN entities t ON t.id = e.target_id
        ORDER BY e.weight DESC LIMIT ?""", (limit,))]
    return {"entities": entities, "relationships": edges}


def _prompt_id(text):
    return hashlib.sha1(text.encode()).hexdigest()[:16]


STARTERS = [
    "What happened today that you want to remember a year from now?",
    "Who did you spend time with recently, and how did it leave you feeling?",
    "What's one thing on your mind that you haven't said out loud yet?",
]


def rule_based_suggestions(conn, max_prompts=4):
    """Prompts derived directly from graph edges and node recency — no AI needed."""
    suggestions = []

    # Dormant important entities: mentioned often, but not recently.
    rows = conn.execute("""
        SELECT name, type, mention_count,
               CAST(julianday('now') - julianday(last_seen) AS INTEGER) AS days_quiet
        FROM entities
        WHERE mention_count >= 2 AND julianday('now') - julianday(last_seen) >= 7
        ORDER BY mention_count DESC LIMIT 2""").fetchall()
    for r in rows:
        who = r["name"]
        if r["type"] == "person":
            suggestions.append(f"You haven't written about {who} in {r['days_quiet']} days — how are things between you two?")
        else:
            suggestions.append(f"It's been {r['days_quiet']} days since {who} came up — what's the latest there?")

    # Strongest edges: recurring pairs invite relationship reflection.
    rows = conn.execute("""
        SELECT s.name AS a, t.name AS b, e.label, e.weight
        FROM edges e
        JOIN entities s ON s.id = e.source_id
        JOIN entities t ON t.id = e.target_id
        WHERE e.weight >= 2
        ORDER BY e.weight DESC LIMIT 2""").fetchall()
    for r in rows:
        suggestions.append(
            f"{r['a']} and {r['b']} keep showing up together in your entries "
            f"({r['label']}) — what does that connection mean to you right now?")

    # Newest entity: invite elaboration.
    row = conn.execute("""
        SELECT name, type FROM entities
        WHERE mention_count = 1 ORDER BY first_seen DESC LIMIT 1""").fetchone()
    if row:
        suggestions.append(f"You mentioned {row['name']} for the first time recently — tell the story of how they came into the picture.")

    return suggestions[:max_prompts]


def refresh_prompts(conn, ai_module=None, want_ai=True):
    """Fill the prompts table with fresh suggestions; returns active prompts."""
    entity_count = conn.execute("SELECT COUNT(*) c FROM entities").fetchone()["c"]

    texts = []
    if entity_count == 0:
        texts = [(t, "starter") for t in STARTERS]
    else:
        texts = [(t, "graph") for t in rule_based_suggestions(conn)]
        if want_ai and ai_module and ai_module.ai_available():
            for t in ai_module.generate_prompts(summary_for_ai(conn), n=3):
                texts.append((t, "ai"))
        if not texts:
            texts = [(STARTERS[0], "starter")]

    for text, source in texts:
        conn.execute(
            "INSERT OR IGNORE INTO prompts (id, text, source) VALUES (?, ?, ?)",
            (_prompt_id(text), text, source))
    conn.commit()

    return [dict(r) for r in conn.execute("""
        SELECT id, text, source, created_at FROM prompts
        WHERE dismissed = 0 ORDER BY created_at DESC, source LIMIT 6""")]
