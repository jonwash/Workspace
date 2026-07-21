# AGENTS.md — Echo

A README for coding agents working in this repository. Human context is in
[`README.md`](README.md); the product spec is in [`journal/spec/`](journal/spec/).

## Start here

- The product is **Echo**, an AI journaling app, in [`journal/`](journal/).
- The source of truth for *what to build and how "done" is judged* is
  [`journal/spec/product_spec.yaml`](journal/spec/product_spec.yaml)
  (narrative rationale: [`journal/spec/PRD.md`](journal/spec/PRD.md)).
- API and data contracts are authoritative:
  [`journal/spec/openapi.yaml`](journal/spec/openapi.yaml) and
  [`journal/spec/schemas/`](journal/spec/schemas/).
- The `legacy/` folder is an unrelated older project — do not modify it.

## Build & test (run from `journal/`)

```bash
# Run the app (zero install)
python3 app.py                       # http://localhost:8777

# Seed demo data
python3 seed.py --reset

# Evaluation protocol — these are the required gates from product_spec.yaml
python3 -m py_compile app.py ai.py db.py graph.py gamification.py seed.py
python3 tests/acceptance.py          # stdlib only; boots server, asserts acceptance criteria
python3 spec/validate_spec.py spec/product_spec.yaml   # needs: pip install pyyaml jsonschema
```

`tests/acceptance.py` runs deterministically in offline (fallback) mode — no key
or network needed. It is the executable oracle for the acceptance criteria; keep
it green.

## Working agreements

- **No new runtime dependencies.** The shipped app is Python standard library +
  SQLite only. `anthropic` is optional (enables live AI); `pyyaml`/`jsonschema`
  are dev-only (spec validation). Adding anything to the runtime path is a
  `forbidden_action` in the spec and needs human approval.
- **Never modify, fabricate, or "improve" a user's entry text.** The AI layer
  only extracts, reflects, and prompts.
- **Never log or return secrets or raw entry content.** `ANTHROPIC_API_KEY` is
  read from the environment only.
- **Keep contract and code in sync.** Any endpoint or payload change updates
  `openapi.yaml` and the relevant `schemas/` file in the same PR.
- **Autonomy is semi-autonomous:** you may modify code, run the evaluation
  protocol, and open a PR. Do not merge or deploy.

## Definition of done

- All three evaluation commands above pass.
- `openapi.yaml` and `schemas/` reflect any interface/data change.
- `PRD.md` updated if intent, scope, or non-goals changed.
- New user-facing behavior has a matching assertion in `tests/acceptance.py`.
