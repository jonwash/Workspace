"""Seed Echo with a month of rich, typed entries — for demos and first looks.

    python3 seed.py            # fills the default journal.db
    python3 seed.py --reset    # wipe first, then seed
    JOURNAL_DB=demo.db python3 seed.py --reset

Entries are written straight into the database with hand-authored entities and
relationships (no AI or API key required), so the knowledge graph and progress
dashboard look alive the moment you open the app. Dates are relative to today,
so the streak and 14-day chart always land in range.
"""

import argparse
import os
from datetime import date, timedelta

import db
import gamification
import graph


# (days_ago, title, content, mood, [(entity, type)...], [(a, b, label)...])
ENTRIES = [
    (29, "First week back", "First Monday back after the trip. Sat down with Priya to scope Project Phoenix "
     "properly. She's sharp — caught two assumptions I'd baked in without noticing.", 4,
     [("Priya", "person"), ("Project Phoenix", "project")],
     [("Priya", "Project Phoenix", "leads")]),
    (27, "Run then rain", "Long run around Lake Merritt before the rain came in. Cleared my head. Kept "
     "thinking about how to frame the Phoenix pitch for Marcus.", 4,
     [("Lake Merritt", "place"), ("Running", "activity"), ("Project Phoenix", "project"), ("Marcus", "person")],
     [("Running", "Lake Merritt", "happens at"), ("Marcus", "Project Phoenix", "sponsors")]),
    (26, "Dad's birthday call", "Called Dad for his birthday. He's taken up woodworking, of all things. "
     "We talked for an hour, which we never do. Felt good.", 5,
     [("Dad", "person"), ("Woodworking", "activity")],
     [("Dad", "Woodworking", "took up")]),
    (24, "Pitch day", "Pitched Project Phoenix to Marcus and the team at the Ferry Building office. Nervous "
     "going in, but Priya and I had rehearsed it cold. Got the green light.", 5,
     [("Project Phoenix", "project"), ("Marcus", "person"), ("Ferry Building", "place"), ("Priya", "person")],
     [("Priya", "Project Phoenix", "leads"), ("Marcus", "Project Phoenix", "approved")]),
    (23, "Quiet one", "Nothing much today. Groceries, laundry, a little reading. Sometimes an even day is "
     "exactly what you need after a big one.", 3,
     [("Reading", "activity")], []),
    (21, "Coffee with Sarah", "Coffee with Sarah at Blue Bottle. She's thinking about leaving her job. I mostly "
     "listened. Hard to watch a friend at a crossroads and not just hand them an answer.", 3,
     [("Sarah", "person"), ("Blue Bottle", "place")],
     [("Sarah", "Blue Bottle", "met at")]),
    (20, "Phoenix kickoff", "Real kickoff for Project Phoenix. Marcus pulled in Devi from the data team — she "
     "already has ideas about the pipeline. Momentum feels good.", 4,
     [("Project Phoenix", "project"), ("Marcus", "person"), ("Devi", "person")],
     [("Devi", "Project Phoenix", "works on"), ("Marcus", "Project Phoenix", "sponsors")]),
    (18, "Rough morning", "Slept badly, snapped at someone I shouldn't have. Went for a run at Lake Merritt "
     "to reset. Owe an apology tomorrow.", 2,
     [("Running", "activity"), ("Lake Merritt", "place")],
     [("Running", "Lake Merritt", "happens at")]),
    (17, "Made it right", "Apologized to Devi first thing. She was gracious about it. Reminded me that the "
     "work is only ever as good as how you treat the people doing it.", 4,
     [("Devi", "person"), ("Project Phoenix", "project")],
     [("Devi", "Project Phoenix", "works on")]),
    (15, "Dinner with Priya", "Dinner with Priya and her partner. First time we've talked about something other "
     "than Phoenix in weeks. She's the best kind of collaborator — becomes a friend.", 5,
     [("Priya", "person")], []),
    (14, "Sarah decided", "Sarah called — she's leaving the job. Scared and relieved in the same breath. I "
     "told her the scared part usually means it matters.", 4,
     [("Sarah", "person")], []),
    (12, "Halfway", "Phoenix hit its halfway checkpoint. Devi's pipeline is holding up under real data. "
     "Marcus stopped by just to say it's the cleanest launch he's seen. Rare praise from him.", 5,
     [("Project Phoenix", "project"), ("Devi", "person"), ("Marcus", "person")],
     [("Devi", "Project Phoenix", "works on"), ("Marcus", "Project Phoenix", "sponsors")]),
    (11, "Woodworking with Dad", "Dad mailed me a cutting board he made. Actually beautiful. Called to thank him "
     "and we ended up planning a visit. Woodworking gave us a language.", 5,
     [("Dad", "person"), ("Woodworking", "activity")],
     [("Dad", "Woodworking", "took up")]),
    (9, "Lake and thinking", "Run at Lake Merritt. Thought about Sarah, about how brave it is to walk away from "
     "something steady. Hope I'd have the nerve.", 3,
     [("Running", "activity"), ("Lake Merritt", "place"), ("Sarah", "person")],
     [("Running", "Lake Merritt", "happens at")]),
    (7, "Launch week begins", "Launch week for Project Phoenix. The Ferry Building office is buzzing. Priya, Devi "
     "and I did a final walkthrough. Everything green.", 4,
     [("Project Phoenix", "project"), ("Ferry Building", "place"), ("Priya", "person"), ("Devi", "person")],
     [("Priya", "Project Phoenix", "leads"), ("Devi", "Project Phoenix", "works on")]),
    (5, "It shipped", "Project Phoenix shipped. Months of work, live in the world. Marcus took the whole "
     "team out. I stood there a little stunned, honestly. We did this.", 5,
     [("Project Phoenix", "project"), ("Marcus", "person")],
     [("Marcus", "Project Phoenix", "sponsors")]),
    (4, "The quiet after", "The day after a launch is strange — all that momentum with nowhere to go. Took "
     "myself to Blue Bottle and just sat with it.", 3,
     [("Blue Bottle", "place")], []),
    (3, "Sarah's new start", "Sarah started her new thing. Sent me a photo from her first day, grinning. The "
     "scared-brave gamble is paying off. So happy for her.", 5,
     [("Sarah", "person")], []),
    (2, "Run and reflect", "Long slow run at Lake Merritt. Trying to figure out what's next now that Phoenix "
     "is out. Priya thinks there's a second act. Maybe she's right.", 4,
     [("Running", "activity"), ("Lake Merritt", "place"), ("Project Phoenix", "project"), ("Priya", "person")],
     [("Running", "Lake Merritt", "happens at"), ("Priya", "Project Phoenix", "leads")]),
    (1, "Dinner, planning", "Dinner with Priya and Devi to sketch what comes after Phoenix. Notebook full of "
     "half-ideas. This is my favorite part — the blank page before the thing exists.", 5,
     [("Priya", "person"), ("Devi", "person"), ("Project Phoenix", "project")],
     [("Devi", "Project Phoenix", "works on"), ("Priya", "Project Phoenix", "leads")]),
    (0, "Today", "Quiet, good day. Wrote a bit, walked to Blue Bottle, called Dad. The kind of ordinary "
     "I want more of.", 4,
     [("Blue Bottle", "place"), ("Dad", "person")], []),
]

REFLECTIONS = {
    24: "A pitch you rehearsed cold, and it landed — that preparation was its own kind of confidence. What did you notice in yourself walking out of that room?",
    17: "Repair is harder than being right, and you chose it first thing. What made the apology feel possible this time?",
    5: "Months of work, suddenly real in the world — of course you were stunned. Now that the momentum has nowhere to go, what do you want to carry into whatever's next?",
}


def seed(reset=False):
    db.init()
    conn = db.connect()
    if reset:
        for tbl in ("entity_mentions", "edges", "entities", "entries", "achievements", "prompts"):
            conn.execute(f"DELETE FROM {tbl}")
        conn.commit()

    today = date.today()
    for days_ago, title, content, mood, ents, rels in ENTRIES:
        entry_date = (today - timedelta(days=days_ago)).isoformat()
        reflection = REFLECTIONS.get(days_ago) or (
            "Thanks for writing this down. As you re-read it, what stands out most?")
        cur = conn.execute(
            """INSERT INTO entries (entry_date, title, content, mood, word_count, reflection)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (entry_date, title, content, mood, len(content.split()), reflection))
        extraction = {
            "entities": [{"name": n, "type": t} for n, t in ents],
            "relationships": [{"source": a, "target": b, "label": l} for a, b, l in rels],
        }
        graph.upsert_extraction(conn, cur.lastrowid, extraction)

    gamification.check_achievements(conn)
    entries = conn.execute("SELECT COUNT(*) c FROM entries").fetchone()["c"]
    entities = conn.execute("SELECT COUNT(*) c FROM entities").fetchone()["c"]
    edges = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]
    conn.close()
    print(f"Seeded {entries} entries, {entities} entities, {edges} relationships "
          f"into {db.DB_PATH}")
    print("Run `python3 app.py` and open http://localhost:8777")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seed Echo with demo entries.")
    ap.add_argument("--reset", action="store_true", help="wipe existing data first")
    seed(reset=ap.parse_args().reset)
