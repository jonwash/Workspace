"""Acceptance tests for Echo — the executable evaluation oracle.

    python3 tests/acceptance.py          # from the journal/ directory

Pure standard library. Boots app.py on a throwaway SQLite DB and an unused port,
exercises the real HTTP API, and asserts the acceptance criteria enumerated in
spec/product_spec.yaml. Each assertion prints its AC id. Exits non-zero on any
failure so it can gate CI.

This deliberately runs in offline/fallback mode (no ANTHROPIC_API_KEY) so it is
deterministic and needs no network or key — matching AC-6.2.
"""

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(HERE)

_passed = 0
_failed = 0


def check(ac, condition, detail=""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  ✓ {ac}")
    else:
        _failed += 1
        print(f"  ✗ {ac}  {detail}")


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Client:
    def __init__(self, base):
        self.base = base

    def request(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                ctype = r.headers.get("Content-Type", "")
                return r.status, (json.loads(raw or "null") if "json" in ctype else raw)
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or "null")

    def get(self, p): return self.request("GET", p)
    def post(self, p, b=None): return self.request("POST", p, b)
    def delete(self, p): return self.request("DELETE", p)


def wait_until_up(client, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            status, _ = client.get("/api/stats")
            if status == 200:
                return True
        except Exception:
            pass
        time.sleep(0.15)
    return False


def main():
    port = _free_port()
    tmp = tempfile.mkdtemp(prefix="echo-accept-")
    db_path = os.path.join(tmp, "test.db")
    env = dict(os.environ)
    env["JOURNAL_DB"] = db_path
    env["JOURNAL_PORT"] = str(port)
    env.pop("ANTHROPIC_API_KEY", None)  # force deterministic fallback mode

    proc = subprocess.Popen([sys.executable, "app.py"], cwd=APP_DIR, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        c = Client(f"http://127.0.0.1:{port}")
        if not wait_until_up(c):
            print("FAIL — server did not start")
            return 1

        # AC-6.1 / AC-6.2: SPA served, endpoints work with no key
        status, _ = c.get("/")
        check("AC-6.1 SPA served at /", status == 200, f"status={status}")

        # US-1: create + reflection
        t0 = time.monotonic()
        status, res = c.post("/api/entries", {
            "content": "Coffee with Sarah at Blue Bottle to plan Project Phoenix.",
            "mood": 4, "title": "Kickoff"})
        save_ms = (time.monotonic() - t0) * 1000
        check("AC-1.1 create returns 200 + entry id",
              status == 200 and isinstance(res.get("entry", {}).get("id"), int), f"status={status}")
        check("AC-1.2 reflection present", bool(res.get("reflection")))
        check("AC-2.1 entities extracted with valid type",
              any(e["type"] in ("person", "place", "organization", "project",
                                "activity", "event", "other")
                  for e in res["entry"]["entities"]),
              "no typed entities")
        entry_id = res["entry"]["id"]

        # perf budget (fallback save round-trip)
        check("perf save_roundtrip_fallback_ms < 500", save_ms < 500, f"{save_ms:.0f}ms")

        # AC-1.3: empty content rejected
        status, res = c.post("/api/entries", {"content": "   "})
        check("AC-1.3 empty content -> 400 + error",
              status == 400 and "error" in res, f"status={status}")

        # AC-1.4: bad mood/date coerced, not rejected
        status, res = c.post("/api/entries", {"content": "Second entry about Sarah.",
                                              "mood": 99, "entry_date": "not-a-date"})
        check("AC-1.4 bad mood/date coerced (200)", status == 200, f"status={status}")
        check("AC-1.4 mood coerced to null", res["entry"]["mood"] is None)

        # AC-2.2: recurrence increments, no duplicate
        _, graph = c.get("/api/graph")
        sarah = [n for n in graph["nodes"] if n["name"].lower() == "sarah"]
        check("AC-2.2 recurring entity not duplicated", len(sarah) == 1, f"found {len(sarah)}")
        check("AC-2.2 mention_count incremented", sarah and sarah[0]["mention_count"] >= 2,
              f"count={sarah[0]['mention_count'] if sarah else 'n/a'}")

        # AC-2.3: co-mention edge with label + weight
        check("AC-2.3 edges have label + weight>=1",
              all("label" in l and l["weight"] >= 1 for l in graph["links"]) and len(graph["links"]) >= 1,
              f"{len(graph['links'])} links")

        # US-3: entity story
        eid = sarah[0]["id"]
        t0 = time.monotonic()
        status, story = c.get(f"/api/entities/{eid}")
        read_ms = (time.monotonic() - t0) * 1000
        check("AC-3.1 entity story has connections + entries",
              status == 200 and "connections" in story and len(story["entries"]) >= 2,
              f"entries={len(story.get('entries', []))}")
        check("AC-3.2 since = earliest mention",
              story["since"] == min(e["entry_date"] for e in story["entries"]))
        status, res = c.get("/api/entities/999999")
        check("AC-3.3 unknown entity -> 404", status == 404 and "error" in res, f"status={status}")
        check("perf read_endpoint_ms < 200", read_ms < 200, f"{read_ms:.0f}ms")

        # US-4: stats shape + achievements
        status, stats = c.get("/api/stats")
        check("AC-4.1 stats shape",
              stats["level"]["level"] in range(1, 12)
              and len(stats["achievements"]) == 11
              and len(stats["history"]) == 14,
              "unexpected stats shape")
        check("AC-4.3 first_entry unlocked",
              any(a["key"] == "first_entry" and a["unlocked"] for a in stats["achievements"]))
        check("AC-4.1 streak.current >= 1 after writing today", stats["streak"]["current"] >= 1)

        # US-5: prompts (graph-derived, dismissable)
        status, p = c.get("/api/prompts")
        check("AC-5.1 prompts have id/text/source",
              all({"id", "text", "source"} <= set(pr) for pr in p["prompts"]) and "ai" in p)
        check("AC-5.4 non-empty prompt list", len(p["prompts"]) >= 1)
        if p["prompts"]:
            pid = p["prompts"][0]["id"]
            status, res = c.post(f"/api/prompts/{pid}/dismiss")
            check("AC-5.3 dismiss returns ok", status == 200 and res.get("ok") is True)
            _, p2 = c.get("/api/prompts")
            check("AC-5.3 dismissed prompt hidden",
                  pid not in {pr["id"] for pr in p2["prompts"]})

        # US-4 / F4: delete cascades
        status, res = c.delete(f"/api/entries/{entry_id}")
        check("AC delete entry -> ok", status == 200 and res.get("ok") is True)
        status, _ = c.get(f"/api/entries/{entry_id}")
        check("deleted entry -> 404", status == 404)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    print(f"\n{_passed} passed, {_failed} failed")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
