"""Echo — an AI journaling app with a knowledge graph of your life.

Run:  python3 app.py  (then open http://localhost:8777)

Zero required dependencies (Python stdlib + SQLite). Set ANTHROPIC_API_KEY and
`pip install anthropic` to enable Claude-powered entity extraction, reflections,
and personalized prompts; without it, deterministic fallbacks are used.
"""

import json
import os
import re
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import ai
import db
import gamification
import graph

PORT = int(os.environ.get("JOURNAL_PORT", "8777"))
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

_write_lock = threading.Lock()


def create_entry(payload):
    content = (payload.get("content") or "").strip()
    if not content:
        return {"error": "Entry content is required."}, 400

    title = (payload.get("title") or "").strip() or None
    mood = payload.get("mood")
    mood = int(mood) if mood and str(mood).isdigit() and 1 <= int(mood) <= 5 else None
    entry_date = payload.get("entry_date") or date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", entry_date):
        entry_date = date.today().isoformat()
    word_count = len(content.split())

    with _write_lock:
        conn = db.connect()
        try:
            known = [r["name"] for r in conn.execute(
                "SELECT name FROM entities ORDER BY mention_count DESC LIMIT 100")]
            extraction = ai.extract(content, known)

            cur = conn.execute(
                """INSERT INTO entries (entry_date, title, content, mood, word_count, reflection)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (entry_date, title, content, mood, word_count,
                 extraction.get("reflection")))
            entry_id = cur.lastrowid
            new_entities = graph.upsert_extraction(conn, entry_id, extraction)
            new_achievements = gamification.check_achievements(conn)

            return {
                "entry": get_entry(conn, entry_id),
                "reflection": extraction.get("reflection"),
                "new_entities": new_entities,
                "new_achievements": [
                    {"key": k, "emoji": gamification.ACHIEVEMENTS[k][0],
                     "name": gamification.ACHIEVEMENTS[k][1]}
                    for k in new_achievements
                ],
                "stats": gamification.stats(conn),
            }, 200
        finally:
            conn.close()


def get_entry(conn, entry_id):
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if not row:
        return None
    entry = dict(row)
    entry["entities"] = [dict(r) for r in conn.execute("""
        SELECT e.id, e.name, e.type FROM entity_mentions m
        JOIN entities e ON e.id = m.entity_id WHERE m.entry_id = ?""", (entry_id,))]
    return entry


def list_entries(conn):
    rows = conn.execute("""
        SELECT id, created_at, entry_date, title, mood, word_count,
               substr(content, 1, 240) AS preview
        FROM entries ORDER BY entry_date DESC, id DESC LIMIT 200""").fetchall()
    entries = []
    for row in rows:
        e = dict(row)
        e["entities"] = [dict(r) for r in conn.execute("""
            SELECT en.id, en.name, en.type FROM entity_mentions m
            JOIN entities en ON en.id = m.entity_id WHERE m.entry_id = ?""", (row["id"],))]
        entries.append(e)
    return entries


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the console quiet

    # ------------------------------------------------------------- helpers
    def _json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    def _serve_index(self):
        path = os.path.join(STATIC_DIR, "index.html")
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # -------------------------------------------------------------- routes
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self._serve_index()

        conn = db.connect()
        try:
            if path == "/api/entries":
                return self._json({"entries": list_entries(conn)})
            match = re.fullmatch(r"/api/entries/(\d+)", path)
            if match:
                entry = get_entry(conn, int(match.group(1)))
                return self._json(entry or {"error": "not found"},
                                  200 if entry else 404)
            if path == "/api/graph":
                return self._json(graph.get_graph(conn))
            if path == "/api/stats":
                return self._json(gamification.stats(conn))
            if path == "/api/prompts":
                prompts = graph.refresh_prompts(conn, ai_module=ai)
                return self._json({"prompts": prompts, "ai": ai.ai_available()})
            return self._json({"error": "not found"}, 404)
        finally:
            conn.close()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/entries":
            result, status = create_entry(self._read_json())
            return self._json(result, status)

        match = re.fullmatch(r"/api/prompts/([0-9a-f]+)/dismiss", path)
        if match:
            conn = db.connect()
            try:
                conn.execute("UPDATE prompts SET dismissed = 1 WHERE id = ?",
                             (match.group(1),))
                conn.commit()
                return self._json({"ok": True})
            finally:
                conn.close()

        return self._json({"error": "not found"}, 404)

    def do_DELETE(self):
        match = re.fullmatch(r"/api/entries/(\d+)", urlparse(self.path).path)
        if not match:
            return self._json({"error": "not found"}, 404)
        with _write_lock:
            conn = db.connect()
            try:
                conn.execute("DELETE FROM entries WHERE id = ?", (match.group(1),))
                conn.commit()
                return self._json({"ok": True})
            finally:
                conn.close()


def main():
    db.init()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    mode = "Claude-powered" if ai.ai_available() else "offline fallback"
    print(f"Echo journal running at http://localhost:{PORT}  (AI: {mode})")
    server.serve_forever()


if __name__ == "__main__":
    main()
