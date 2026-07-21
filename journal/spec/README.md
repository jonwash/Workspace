# Echo — product spec

An **agent-consumable product spec**: structured, versioned, and test-linked, so
a coding agent (or a person) can discover intent, act, verify against a real
evaluation protocol, and stop. Built as a multi-layer bundle.

| Layer | File | What it is |
|---|---|---|
| **Narrative** (human-first) | [`PRD.md`](PRD.md) | Problem, personas, flows, success metrics, rationale |
| **Machine spec** (agent-first) | [`product_spec.yaml`](product_spec.yaml) | Autonomy, scope, user stories with acceptance criteria, UX flows (state/transition/oracle), evaluation protocol |
| **API contract** | [`openapi.yaml`](openapi.yaml) | OpenAPI 3.1 for all 8 endpoints (authoritative) |
| **Data contracts** | [`schemas/`](schemas/) | JSON Schema (2020-12) for Entry, Entity, Edge, and the extraction event |
| **Spec validation** | [`product_spec.schema.json`](product_spec.schema.json) + [`validate_spec.py`](validate_spec.py) | Validates the spec's structure + cross-file references |
| **Executable acceptance** | [`../tests/acceptance.py`](../tests/acceptance.py) | Boots the app and asserts every acceptance criterion against the live API |
| **Repo binding** | [`../../AGENTS.md`](../../AGENTS.md) | Setup, test commands, working agreements, definition of done |

## Verify the whole spec (from `journal/`)

```bash
python3 -m py_compile app.py ai.py db.py graph.py gamification.py seed.py
python3 tests/acceptance.py                              # 24 checks, offline/deterministic
pip install pyyaml jsonschema                            # dev-only, for the next line
python3 spec/validate_spec.py spec/product_spec.yaml     # structure + cross-file refs
```

All three are the required gates declared in `product_spec.yaml` under
`evaluation.commands` — the spec judges itself by commands that actually run.

## Design principle

The methodology this follows (structured contracts + executable acceptance +
operational policy) scales to enterprise systems with perf gates, provenance,
and formal telemetry. Echo is a small, single-user, zero-dependency app, so
those heavier controls are represented as **"applies at scale"** notes rather
than cargo-culted in. The spec is calibrated to the product it describes.
