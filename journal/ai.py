"""AI layer: entity/relationship extraction, reflections, and prompt generation.

Uses the Anthropic SDK (claude-opus-4-8) when ANTHROPIC_API_KEY is set and the
`anthropic` package is installed. Otherwise falls back to deterministic
heuristics so the app works fully offline — just with less nuance.
"""

import json
import os
import re

MODEL = "claude-opus-4-8"

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
        _client = anthropic.Anthropic()
        return _client
    except Exception:
        return None


def ai_available():
    return _get_client() is not None


# ---------------------------------------------------------------- extraction

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["person", "place", "organization", "project",
                                 "activity", "event", "other"],
                    },
                },
                "required": ["name", "type"],
                "additionalProperties": False,
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "label": {"type": "string"},
                },
                "required": ["source", "target", "label"],
                "additionalProperties": False,
            },
        },
        "reflection": {"type": "string"},
    },
    "required": ["entities", "relationships", "reflection"],
    "additionalProperties": False,
}

EXTRACTION_SYSTEM = """You analyze a personal journal entry. Extract:
1. entities: the significant recurring things in the writer's life — people, \
places, organizations, projects, activities, events. Use the shortest natural \
name (e.g. "Sarah", "the gym", "Project Phoenix"). Skip generic nouns, dates, \
and the writer themself.
2. relationships: meaningful connections stated or implied between those \
entities, with a short lowercase label like "works with", "lives in", \
"argued with", "part of".
3. reflection: 2-3 warm, non-judgmental sentences back to the writer that help \
them process what they wrote, ending with one gentle follow-up question. Speak \
directly to them ("you")."""


def extract(text, known_entities=None):
    """Return {entities, relationships, reflection} for a journal entry."""
    client = _get_client()
    if client is None:
        return _extract_fallback(text, known_entities or [])

    known = ", ".join(known_entities[:60]) if known_entities else "(none yet)"
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=EXTRACTION_SYSTEM,
            output_config={"format": {"type": "json_schema", "schema": EXTRACTION_SCHEMA}},
            messages=[{
                "role": "user",
                "content": (
                    f"Entities already known from past entries (reuse these exact "
                    f"names when the entry refers to them): {known}\n\n"
                    f"Journal entry:\n{text}"
                ),
            }],
        )
        if response.stop_reason == "refusal":
            return _extract_fallback(text, known_entities or [])
        raw = next(b.text for b in response.content if b.type == "text")
        data = json.loads(raw)
        data.setdefault("entities", [])
        data.setdefault("relationships", [])
        data.setdefault("reflection", "")
        return data
    except Exception:
        return _extract_fallback(text, known_entities or [])


STOPWORDS = {
    "I", "The", "A", "An", "It", "My", "We", "He", "She", "They", "But", "And",
    "So", "Then", "This", "That", "Today", "Yesterday", "Tomorrow", "When",
    "After", "Before", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", "Sunday", "January", "February", "March", "April", "May",
    "June", "July", "August", "September", "October", "November", "December",
    "If", "In", "On", "At", "There", "Here", "Also", "However", "Maybe",
    "Not", "No", "Yes", "Everything", "Everyone", "Something", "Someone",
}


def _extract_fallback(text, known_entities):
    """Heuristic extraction: capitalized words mid-sentence + known-entity matches."""
    found = {}

    # Re-match entities we already know about, case-insensitively.
    for name in known_entities:
        if re.search(r"\b" + re.escape(name) + r"\b", text, re.IGNORECASE):
            found[name.lower()] = {"name": name, "type": "other"}

    # Capitalized tokens (or runs like "Golden Gate Park") not at sentence start.
    for match in re.finditer(r"(?<![.!?]\s)(?<!^)(?<!\n)\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b", text):
        name = match.group(1).strip()
        if name in STOPWORDS or name.split()[0] in STOPWORDS or len(name) < 3:
            continue
        found.setdefault(name.lower(), {"name": name, "type": "person"})

    entities = list(found.values())[:12]

    # Co-occurrence relationships between everything found in the same entry.
    relationships = []
    names = [e["name"] for e in entities]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            relationships.append({"source": names[i], "target": names[j],
                                  "label": "appears with"})

    reflection = (
        "Thanks for taking the time to write this down — capturing it is how the "
        "processing starts. As you re-read what you wrote, what feeling stands "
        "out the most?"
    )
    return {"entities": entities, "relationships": relationships[:20],
            "reflection": reflection}


# ------------------------------------------------------------------ prompts

PROMPT_SYSTEM = """You generate journaling prompts for one specific person based \
on their knowledge graph — the people, places, and projects in their life and \
how they connect. Write prompts that reference those specifics by name, invite \
reflection on relationships and change over time, and feel personal rather than \
generic. One sentence each."""


def generate_prompts(graph_summary, n=3):
    """Return up to n personalized prompt strings from a graph summary dict."""
    client = _get_client()
    if client is None:
        return []
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=PROMPT_SYSTEM,
            output_config={"format": {"type": "json_schema", "schema": {
                "type": "object",
                "properties": {"prompts": {"type": "array", "items": {"type": "string"}}},
                "required": ["prompts"],
                "additionalProperties": False,
            }}},
            messages=[{
                "role": "user",
                "content": (
                    f"Knowledge graph of my life:\n{json.dumps(graph_summary, indent=1)}\n\n"
                    f"Write {n} journaling prompts for me."
                ),
            }],
        )
        if response.stop_reason == "refusal":
            return []
        raw = next(b.text for b in response.content if b.type == "text")
        return json.loads(raw).get("prompts", [])[:n]
    except Exception:
        return []
