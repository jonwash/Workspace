"""SQLite storage for the journaling app.

Tables:
  entries          — journal entries
  entities         — people/places/projects/events extracted from entries
  entity_mentions  — which entities appear in which entries
  edges            — knowledge-graph relationships between entities
  achievements     — unlocked gamification badges
  prompts          — AI/graph-generated journaling prompts shown to the user
"""

import os
import sqlite3

DB_PATH = os.environ.get("JOURNAL_DB", os.path.join(os.path.dirname(__file__), "journal.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    entry_date  TEXT NOT NULL,              -- YYYY-MM-DD, the day this entry is about
    title       TEXT,
    content     TEXT NOT NULL,
    mood        INTEGER,                    -- 1..5, optional
    word_count  INTEGER NOT NULL DEFAULT 0,
    reflection  TEXT                        -- AI reflection on the entry
);

CREATE TABLE IF NOT EXISTS entities (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE COLLATE NOCASE,
    type          TEXT NOT NULL DEFAULT 'other',  -- person|place|organization|project|activity|event|other
    first_seen    TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen     TEXT NOT NULL DEFAULT (datetime('now')),
    mention_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS entity_mentions (
    entry_id  INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    PRIMARY KEY (entry_id, entity_id)
);

CREATE TABLE IF NOT EXISTS edges (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id  INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    target_id  INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    label      TEXT NOT NULL DEFAULT 'appears with',
    weight     INTEGER NOT NULL DEFAULT 1,
    last_seen  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (source_id, target_id, label)
);

CREATE TABLE IF NOT EXISTS achievements (
    key         TEXT PRIMARY KEY,
    unlocked_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS prompts (
    id         TEXT PRIMARY KEY,             -- stable key so the same suggestion isn't duplicated
    text       TEXT NOT NULL,
    source     TEXT NOT NULL DEFAULT 'graph',-- graph|ai|starter
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    dismissed  INTEGER NOT NULL DEFAULT 0
);
"""


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init():
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
