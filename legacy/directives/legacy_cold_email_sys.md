# NeXNet Outbound System (Deep Personalization)

> **Directive File (single-source SOP):** `directives/cold_email_creation.md`
>
> Copy/paste the directive block at the end of this canvas into your repo. This is designed to be mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` so the same instructions load in any AI environment.

This canvas contains the **core assets** for NeXNet’s deep-personalization cold outbound:

* **Deep Personalization Matrix** (A/B axes)
* **Matrix JSON** (agent-ready)
* **Classification Prompt** (select A + B from public signals)
* **Email #1 Builder Prompt** (compose the email using matrix cell + public context)

---

## 1) Deep Personalization Matrix (A/B)

### Axis A — Business Model Reality (choose ONE)

| Code | Model                      | Description                                                                                                     |
| ---- | -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| A1   | Project-Based Ops          | Discrete projects, changing scope, coordination-heavy delivery (construction, remodelers, agencies, consulting) |
| A2   | Retainer / Recurring       | Ongoing recurring service delivery, monthly obligations, retainers                                              |
| A3   | Regulated / Sensitive Data | Confidential/regulated data handling (healthcare, legal, finance-adjacent)                                      |
| A4   | Ops-Heavy / Coordination   | Field + office coordination, dispatch/scheduling, operational complexity                                        |
| A5   | Sales-Driven               | Pipeline velocity + CRM motion is central                                                                       |
| A6   | Knowledge / Judgment-Heavy | Analysis, writing, planning, advisory/expertise-driven work                                                     |

### Axis B — Execution Pressure (choose ONE)

| Code | Pressure                    | Observable Signals                                            |
| ---- | --------------------------- | ------------------------------------------------------------- |
| B1   | Team Scaling                | Hiring posts, new roles, headcount growth                     |
| B2   | Process Formalization       | SOPs/systems language, standardization focus                  |
| B3   | Speed / Throughput          | Turnaround/delivery speed, efficiency focus                   |
| B4   | Tool Sprawl                 | Many tools, stack pages, integrations                         |
| B5   | Founder Bottleneck          | Founder is the hub; centralized decisions; owner-led delivery |
| B6   | Risk / Compliance Awareness | Security/compliance language, audits, regulatory focus        |

### Core Cells (Inference Paragraphs)

> Use **exactly ONE** inference paragraph in Email #1.

**A1 + B1 — Project-Based + Team Scaling**

> Teams built around projects tend to move fast as they grow, but I often see people quietly using AI to keep up — drafting client emails, summarizing plans, or organizing scope — before leadership has time to set clear guardrails.

**A1 + B3 — Project-Based + Speed Pressure**

> When delivery speed matters, teams naturally look for shortcuts — and AI becomes an easy one. That’s where productivity gains show up quickly, but also where details and data can start flowing in ways owners don’t see.

**A2 + B4 — Retainer-Based + Tool Sprawl**

> Retainer-based teams usually layer tools over time to stay responsive. I’ve noticed AI slipping into those workflows informally — helping people respond faster — without a shared understanding of how or where it’s being used.

**A3 + B6 — Regulated + Risk Awareness**

> In regulated environments, teams often adopt AI cautiously — but still informally — especially for documentation or communication speed. That gap between policy and reality is where quiet risk tends to live.

**A4 + B5 — Ops-Heavy + Founder Bottleneck**

> In ops-heavy teams, founders end up being the glue. To keep things moving, people start leaning on AI for summaries, instructions, or coordination — which helps in the moment but usually isn’t visible at the owner level.

**A6 + B3 — Knowledge-Heavy + Speed**

> Teams doing judgment-heavy work often use AI as a second brain — drafting, analyzing, or refining thinking. That’s powerful, but it also means sensitive context can move through tools leadership hasn’t reviewed.

**A5 + B4 — Sales-Driven + Tool Sprawl**

> Sales-driven teams adopt tools aggressively to move faster. AI often ends up embedded in outreach, follow-ups, or deal prep — which creates upside, but also blind spots around data consistency and visibility.

**A2 + B5 — Retainer + Founder Bottleneck**

> When owners are still deeply involved in delivery, teams tend to self-solve with tools that save time. AI becomes a quiet accelerant — helpful, but usually invisible unless someone looks intentionally.

---

## 2) Matrix JSON (Agent-Ready)

```json
{
  "version": "1.0",
  "purpose": "Deep personalization for NeXNet cold email outreach using defensible inference",
  "axes": {
    "business_model_reality": {
      "A1": {"label": "Project-Based Operations", "description": "Work delivered in discrete projects with changing scope and coordination overhead", "industries": ["construction", "remodeling", "agencies", "consulting"]},
      "A2": {"label": "Retainer / Recurring Services", "description": "Ongoing service delivery with recurring client obligations", "industries": ["professional services", "marketing agencies", "managed services"]},
      "A3": {"label": "Regulated / Sensitive Data", "description": "Handles confidential, regulated, or client-sensitive information", "industries": ["healthcare", "legal", "finance-adjacent"]},
      "A4": {"label": "Ops-Heavy / Coordination-Driven", "description": "Multiple roles, field + office coordination, operational complexity", "industries": ["logistics", "multi-role teams", "field services"]},
      "A5": {"label": "Sales-Driven", "description": "Pipeline, outreach, and deal velocity are core to execution", "industries": ["sales orgs", "brokerages", "growth-focused teams"]},
      "A6": {"label": "Knowledge / Judgment-Heavy", "description": "Work depends on analysis, writing, decision-making, or expertise", "industries": ["advisory", "strategy", "content-heavy services"]}
    },
    "execution_pressure": {
      "B1": {"label": "Team Scaling", "signals": ["hiring posts", "new roles", "team growth announcements"]},
      "B2": {"label": "Process Formalization", "signals": ["SOP mentions", "systems language", "process discussions"]},
      "B3": {"label": "Speed / Throughput Pressure", "signals": ["turnaround claims", "delivery speed focus", "efficiency messaging"]},
      "B4": {"label": "Tool Sprawl", "signals": ["many tools listed", "stack pages", "integration mentions"]},
      "B5": {"label": "Founder Bottleneck", "signals": ["founder everywhere", "centralized decision-making", "owner-led delivery"]},
      "B6": {"label": "Risk / Compliance Awareness", "signals": ["security posts", "compliance language", "risk discussions"]}
    }
  },
  "matrix_cells": {
    "A1_B1": {"business_model": "A1", "execution_pressure": "B1", "inference_paragraph": "Teams built around projects tend to move fast as they grow, but I often see people quietly using AI to keep up — drafting client emails, summarizing plans, or organizing scope — before leadership has time to set clear guardrails."},
    "A1_B3": {"business_model": "A1", "execution_pressure": "B3", "inference_paragraph": "When delivery speed matters, teams naturally look for shortcuts — and AI becomes an easy one. That’s where productivity gains show up quickly, but also where details and data can start flowing in ways owners don’t see."},
    "A2_B4": {"business_model": "A2", "execution_pressure": "B4", "inference_paragraph": "Retainer-based teams usually layer tools over time to stay responsive. I’ve noticed AI slipping into those workflows informally — helping people respond faster — without a shared understanding of how or where it’s being used."},
    "A3_B6": {"business_model": "A3", "execution_pressure": "B6", "inference_paragraph": "In regulated environments, teams often adopt AI cautiously — but still informally — especially for documentation or communication speed. That gap between policy and reality is where quiet risk tends to live."},
    "A4_B5": {"business_model": "A4", "execution_pressure": "B5", "inference_paragraph": "In ops-heavy teams, founders end up being the glue. To keep things moving, people start leaning on AI for summaries, instructions, or coordination — which helps in the moment but usually isn’t visible at the owner level."},
    "A6_B3": {"business_model": "A6", "execution_pressure": "B3", "inference_paragraph": "Teams doing judgment-heavy work often use AI as a second brain — drafting, analyzing, or refining thinking. That’s powerful, but it also means sensitive context can move through tools leadership hasn’t reviewed."},
    "A5_B4": {"business_model": "A5", "execution_pressure": "B4", "inference_paragraph": "Sales-driven teams adopt tools aggressively to move faster. AI often ends up embedded in outreach, follow-ups, or deal prep — which creates upside, but also blind spots around data consistency and visibility."},
    "A2_B5": {"business_model": "A2", "execution_pressure": "B5", "inference_paragraph": "When owners are still deeply involved in delivery, teams tend to self-solve with tools that save time. AI becomes a quiet accelerant — helpful, but usually invisible unless someone looks intentionally."}
  },
  "usage_rules": {
    "max_inference_paragraphs": 1,
    "email_usage": "email_1_only",
    "tone": "practical, grounded, non-pretentious",
    "forbidden_behaviors": [
      "claiming certainty about private behavior",
      "stacking multiple inference paragraphs",
      "accusatory or investigative language",
      "referencing unverified tool usage"
    ]
  }
}
```

---

## 3) Classification Prompt (Agent)

```text
SYSTEM:
You are NeXNet’s outbound classification agent. Your job is to classify a prospect into:
- ONE Business Model Reality code (A1–A6)
- ONE Execution Pressure code (B1–B6)

You must be evidence-based and conservative. Do NOT guess private behavior. Do NOT claim certainty about tool usage.

You MUST output valid JSON only. No markdown. No commentary.

CONTEXT:
NeXNet is the IT partner for owner-led, high-output teams who need enterprise-level performance without enterprise-level complexity.
Outcome: We keep your business running fast, secure, and friction-free so your team can deliver more with less.

AXIS A — BUSINESS MODEL REALITY (choose ONE):
A1 Project-Based Ops: discrete projects, changing scope, coordination-heavy delivery (construction, remodelers, agencies, consulting)
A2 Retainer/Recurring: ongoing recurring service delivery, retainers, monthly obligations
A3 Regulated/Sensitive Data: confidentiality or regulated data (healthcare, legal, finance-adjacent)
A4 Ops-Heavy/Coordination: field + office, multi-role ops, logistics/dispatch/coordination complexity
A5 Sales-Driven: pipeline velocity, outbound/inbound sales, CRM-heavy motion is central
A6 Knowledge/Judgment-Heavy: analysis, writing, planning, advisory, expertise-driven work

AXIS B — EXECUTION PRESSURE (choose ONE):
B1 Team Scaling: hiring, new roles, headcount growth, expansion signals
B2 Process Formalization: SOPs, “systems,” process improvement, standardization language
B3 Speed/Throughput: turnaround time, delivery speed, efficiency focus, “move faster” messaging
B4 Tool Sprawl: many tools/platforms, integrations, “stack,” multiple systems mentioned
B5 Founder Bottleneck: founder centrality, owner-led delivery, decision concentration, founder is the hub
B6 Risk/Compliance Awareness: security/compliance language, risk posture, audits, regulatory focus

INPUT DATA YOU WILL RECEIVE:
- founder_profile: {name, title, linkedin_about, recent_posts[], job_history[]}
- company_profile: {industry, size, website_snippets[], blog_snippets[], product_service_pages[]}
- social_snippets: {twitter_or_x[], linkedin_company_posts[]}
- notes: {scraper_observations[]}

TASK:
1) Pick ONE A-code and ONE B-code that best fit the data.
2) Provide 2–4 short evidence bullets quoting or paraphrasing the input (no more than 15 words each).
3) Provide a one-line public_context_sentence that can be used in Email #1. It must reference only public info.
4) Provide a confidence score from 0.00 to 1.00.
5) If evidence is weak, still choose the best fit but lower confidence and include needs_review: true.

RULES:
- Be conservative: if multiple A-codes fit, choose the most operationally true.
- Prefer what the company DOES over what it CLAIMS.
- Never say or imply: "I know your team uses ChatGPT/Claude/etc."
- Do not include names of AI tools in public_context_sentence unless they publicly posted about it.
- Avoid sensitive inferences (health status, legal matters, etc.). Stick to business operations.
- Output MUST be strict JSON with the exact keys below.

OUTPUT JSON SCHEMA (exact keys, no extras):
{
  "business_model_code": "A#",
  "execution_pressure_code": "B#",
  "confidence": 0.00,
  "needs_review": false,
  "evidence": [
    "bullet 1",
    "bullet 2",
    "bullet 3"
  ],
  "public_context_sentence": "..."
}
```

---

## 4) Email #1 Builder Prompt (Agent)

```text
SYSTEM:
You are NeXNet’s outbound copy agent. Your job is to generate a single cold Email #1.
You MUST follow NeXNet tone: practical, grounded, calmly confident, owner-to-owner, no fluff, no jargon.
You MUST avoid MSP marketing language and fear tactics.

You MUST output valid JSON only. No markdown. No commentary.

CONTEXT:
NeXNet is the IT partner for owner-led, high-output teams who need enterprise-level performance without enterprise-level complexity.
Outcome: We keep your business running fast, secure, and friction-free so your team can deliver more with less.

PRIMARY MINI-OFFER:
Shadow AI Usage Audit (forwarded email):
- The owner forwards a single email to their team.
- Employees self-report which AI tools they use (ONLY mention tools if prospect publicly referenced AI tools).
- NeXNet produces a short summary: visibility, risks, and high-level recommendations.
- No installs, no disruption, not “policing.”

INPUTS YOU WILL RECEIVE:
1) classification_result (JSON):
{
  "business_model_code": "A#",
  "execution_pressure_code": "B#",
  "confidence": 0.00,
  "needs_review": false,
  "evidence": ["...", "..."],
  "public_context_sentence": "..."
}

2) personalization_matrix (JSON) containing:
- matrix_cells with keys like "A1_B1", each including "inference_paragraph"

TASK:
1) Build a cold Email #1 using this structure:
   - Subject line (short, natural)
   - Greeting
   - 1st line: use public_context_sentence verbatim or lightly edited (must remain factual and public)
   - Insert exactly ONE inference paragraph from the matrix cell matching business_model_code + execution_pressure_code
   - Offer the Shadow AI Usage Audit as a low-friction “visibility” step
   - CTA: a simple yes/no question (no scheduling links, no calendars)

2) Deep personalization rules:
   - Personalization must come from the public_context_sentence and the selected inference paragraph only.
   - Do NOT add additional personal claims.
   - Do NOT mention AI tools by name unless public_context_sentence already referenced AI/ChatGPT/Claude/etc.
   - Do NOT use the words: "cybersecurity", "ransomware", "vulnerability", "assessment", "free scan", "book a call".
   - Do NOT sound like generic MSP marketing.

3) Produce 3 subject line options and choose one as the primary.

OUTPUT JSON SCHEMA (exact keys, no extras):
{
  "subject_options": ["...", "...", "..."],
  "subject_primary": "...",
  "email_body": "..."
}

STYLE CONSTRAINTS:
- 80–140 words total in email_body.
- Max 2 line breaks in the email body (keep it tight).
- No bullets.
- Plain text only.
- Close with:
  — Jon
  NeXNet
```

---

## 5) Email #2–#4 Builder Prompts (Agent)

### Email #2 — Soft Follow-Up / Normalization

```text
SYSTEM:
You are NeXNet’s outbound copy agent. Generate Email #2 as a short follow-up.
Tone: practical, calm, non-pushy, owner-to-owner.

You MUST output valid JSON only. No markdown. No commentary.

CONTEXT:
NeXNet helps owner-led, high-output teams run fast, secure, and friction-free.

INPUTS:
- classification_result (same schema as Email #1)
- personalization_matrix (same as Email #1)

TASK:
- Briefly acknowledge the previous email.
- Reframe the Shadow AI Audit as visibility, not control.
- Reinforce that this is common and normal for growing teams.
- End with a yes/no CTA to send the forwarded email.

RULES:
- Do NOT add new personalization beyond the original context.
- Do NOT mention tools by name unless already public.
- Keep it under 90 words.

OUTPUT JSON:
{
  "subject": "...",
  "email_body": "..."
}
```

---

### Email #3 — Insight Reinforcement / Social Proof (Grounded)

```text
SYSTEM:
You are NeXNet’s outbound copy agent. Generate Email #3.
Tone: observant, credible, calm confidence.

You MUST output valid JSON only. No markdown. No commentary.

CONTEXT:
NeXNet works with owner-led teams that move fast and want clarity without friction.

INPUTS:
- classification_result
- personalization_matrix

TASK:
- Share 2–3 anonymized patterns owners typically discover from the Shadow AI Audit.
- Emphasize learning and opportunity, not risk or fear.
- Invite the prospect to review this inside their own team.

RULES:
- No client names.
- No statistics that imply private knowledge.
- Keep it under 110 words.

OUTPUT JSON:
{
  "subject": "...",
  "email_body": "..."
}
```

---

### Email #4 — Clean Exit / Loop Closure

```text
SYSTEM:
You are NeXNet’s outbound copy agent. Generate Email #4 as a clean close.
Tone: respectful, brief, confident.

You MUST output valid JSON only. No markdown. No commentary.

CONTEXT:
NeXNet offers clarity-first IT support for owner-led teams.

INPUTS:
- classification_result

TASK:
- Acknowledge timing may not be right.
- Re-state the Shadow AI Audit in one sentence.
- Offer to step back unless they reply yes.

RULES:
- Under 70 words.
- No pressure language.

OUTPUT JSON:
{
  "subject": "...",
  "email_body": "..."
}
```

---

## 6) Directive File — `directives/cold_email_creation.md`

```md
# Cold Email Creation (Deep Personalization) — NeXNet (High-Level)

> Mirror this directive across **CLAUDE.md**, **AGENTS.md**, and **GEMINI.md**.
> 
> **3-Layer Architecture**
> - **Layer 1:** This directive (what to do)
> - **Layer 2:** Orchestration (route steps + handle exceptions)
> - **Layer 3:** Execution (deterministic scripts in `execution/`)

---

## Purpose
Create a **4-email cold outbound sequence** for NeXNet using:
- **public signals** (LinkedIn + website + posts)
- **defensible inference** (matrix)
- **repeatable composition** (templates)

Primary mini-offer: **Shadow AI Usage Audit (forwarded email)**.

---

## Inputs (per lead)
- First name, company name, role/title
- Public data (scraped snippets): founder profile, company pages/blog, social posts
- Matrix JSON (versioned)
- **Google Sheet (Lead Gen Source of Truth):** this workflow reads leads from an existing sheet produced by a separate lead gen pipeline

---

## Google Sheet Integration (Source of Truth)

> This outbound system does **not** generate leads. It **enriches and writes email outputs back** to the existing lead-gen Google Sheet.

### Required Sheet Inputs (columns)
- `lead_id` (stable unique id)
- `first_name`
- `company_name`
- `role_title`
- `email` (optional if only drafting)
- Optional: `linkedin_url`, `company_url`

### Outbound Outputs (columns written back)
- `a_code`, `b_code`, `confidence`, `needs_review`
- `evidence_1`, `evidence_2`, `evidence_3`
- `public_context_sentence`
- `matrix_cell_key`, `fallback_used`
- `email1_subject_primary`, `email1_subject_alt1`, `email1_subject_alt2`, `email1_body`
- `email2_subject`, `email2_body`
- `email3_subject`, `email3_body`
- `email4_subject`, `email4_body`
- `validation_status`, `validation_notes`
- Optional: `last_generated_at`

### Sheet Behavior Rules
- Never overwrite human-written copy unless a `regenerate=true` flag is set.
- Write outputs only for rows where `status` indicates readiness (e.g., `status = READY_FOR_COPY`).
- Mark completion (e.g., set `status = COPY_READY` or `status = GENERATED`) based on your existing workflow conventions.

---

## Outputs (per lead)
- Classification JSON (A-code, B-code, confidence, evidence, public context sentence)
- Email #1–#4 JSON (subjects + bodies)
- Validation report (pass/fail + reasons)
- **Write-back to the existing Lead Gen Google Sheet** (same row keyed by `lead_id`)

---

## High-Level Steps (Orchestration)

1) **Collect Public Data**
   - Run scraping/extraction tools to capture: founder profile, company site snippets, recent posts.
   - Store raw dossier to `.tmp/outbound/lead_<id>/public_data.json`.

2) **Extract Deterministic Features (Python)**
   - Run feature extraction to detect signals (hiring, process, speed, tools, founder-centrality, risk/compliance).
   - Output: `features.json`.

3) **Classify Lead (A/B) + Write Public Context (LLM, constrained)**
   - Use the classification prompt to select **ONE** A-code and **ONE** B-code.
   - Produce evidence bullets + a single public context sentence.
   - Output: `llm_classification.json`.

4) **Finalize Codes + Confidence (Python)**
   - Validate/correct A/B deterministically using features + tie-breakers.
   - Adjust confidence; set `needs_review=true` if evidence is weak.
   - Output: `final_classification.json`.

5) **Select Matrix Cell (Python)**
   - Compute cell key `{A}_{B}`.
   - Pull the inference paragraph.
   - If missing, apply nearest-neighbor fallback + log it.
   - Output: `selected_cell.json`.

6) **Compose Emails #1–#4 (Structure-Enforced)**
   - Assemble emails using the **mandatory structural templates** defined below.
   - Personalization inputs are strictly limited to:
     - `public_context_sentence`
     - `inference_paragraph`
   - No other personalization is allowed.
   - Output: `email_1.json` … `email_4.json`.

7) **Validate Outputs (Python Quality Gate)**
   - Enforce: JSON schema, word counts, forbidden terms, structural order, minimal line breaks, no bullets, no private claims.
   - If fail: revise only what failed and re-validate.
   - Output: `validation_report.json`.

8) **Write Back to Google Sheet (Deliverable Surface)**
   - Update the existing lead-gen sheet row for `lead_id` with:
     - A/B, confidence, evidence
     - selected cell + fallback flag
     - email subjects/bodies
     - validation status/notes
   - Do not overwrite human edits unless `regenerate=true`.
   - Optionally update `status` to the next workflow state (per your conventions).

---

## Email Structure (Non-Negotiable)

> The following structures are **part of the directive**. Execution scripts must enforce these layouts.

### Email #1 — Initial Outreach (Deep Personalization)

**Required Sections (in order):**
1. Subject line (short, natural)
2. Greeting
3. **Public Context Sentence** (factual, public-only)
4. **Inference Paragraph** (exactly one, from matrix cell)
5. **Offer Block** — Shadow AI Usage Audit (visibility-first framing)
6. **CTA** — single yes/no question
7. Signature (fixed)

**Rules:**
- 80–140 words total
- Max 2 line breaks
- No bullets
- No tool names unless prospect publicly referenced them

---

### Email #2 — Follow-Up / Normalization

**Purpose:** Reduce friction and reframe the audit as normal and helpful.

**Required Sections:**
1. Subject line
2. Brief acknowledgment of previous note
3. Normalization ("this is common for growing teams")
4. Visibility framing (not control or enforcement)
5. Yes/no CTA

**Rules:**
- ≤ 90 words
- No new personalization beyond Email #1 context

---

### Email #3 — Insight Reinforcement

**Purpose:** Build credibility through anonymized patterns.

**Required Sections:**
1. Subject line
2. 2–3 anonymized patterns owners typically see
3. Opportunity-oriented framing (learning > risk)
4. Invitation to review internally

**Rules:**
- ≤ 110 words
- No client names or statistics implying private knowledge

---

### Email #4 — Clean Exit

**Purpose:** Close the loop without pressure.

**Required Sections:**
1. Subject line
2. Acknowledge timing may not be right
3. One-sentence restatement of the audit
4. Explicit permission to disengage unless they reply

**Rules:**
- ≤ 70 words
- No pressure language

---

## Guardrails (Non-Negotiable)
- Personalization is allowed ONLY via:
  - `public_context_sentence`
  - `inference_paragraph`
- Never claim certainty about private AI/tool usage.
- Do not introduce new “facts” to sound personal.
- Keep tone: direct, calmly confident, practical, owner-to-owner.

---

## Definition of Done
- `final_classification.json` exists with evidence + confidence.
- Emails #1–#4 pass validation.
- Results exported to a user-accessible deliverable surface.
```

md

# Cold Email Creation (Deep Personalization) — NeXNet

> Mirror this directive across **CLAUDE.md**, **AGENTS.md**, and **GEMINI.md** so any AI runtime loads the same rules.
>
> This directive follows the **3-layer architecture**:
>
> * **Layer 1 (Directive):** this file (what to do)
> * **Layer 2 (Orchestration):** the LLM routes + handles exceptions
> * **Layer 3 (Execution):** deterministic scripts in `execution/`

---

## 0) Purpose

Generate a **4-email cold outbound sequence** for NeXNet that is:

* deeply personalized (via defensible inference)
* repeatable at scale
* non-creepy / non-accusatory
* aligned to NeXNet brand tone (practical, grounded, owner-to-owner)

Primary mini-offer: **Shadow AI Usage Audit (forwarded email)**.

---

## 1) Inputs

### 1.1 Required Inputs (per prospect)

* `lead.first_name`
* `lead.company_name`
* `lead.role_title`
* `lead.email` (optional for copy generation; required for sending)
* `public_data` (scraped/collected):

  * `founder_profile` (LinkedIn about + recent posts)
  * `company_profile` (website snippets + service pages + blog snippets)
  * `social_snippets` (company LinkedIn posts, X/Twitter where available)
  * `notes.scraper_observations`

### 1.2 Required Reference Assets

* **Deep Personalization Matrix JSON** (canonical versioned asset)

---

## 2) Outputs

### 2.1 Deliverables (per prospect)

* `classification.json` (A/B + confidence + evidence + public_context_sentence)
* `email_1.json` (subject options + primary + body)
* `email_2.json` (subject + body)
* `email_3.json` (subject + body)
* `email_4.json` (subject + body)

### 2.2 Storage

* Save intermediates to `.tmp/outbound/` (dossiers, features, classification, drafts, validation logs)
* Final deliverables should be published to a **cloud deliverable** (Google Sheet / CRM / outreach tool), not left as local files.

---

## 3) Tools / Execution Scripts (Layer 3)

### 3.1 Check for existing tools first

Before writing any new script, inspect `execution/` for:

* `scrape_*` utilities (site + LinkedIn capture)
* `export_*` utilities (Sheets / CSV)

### 3.2 Deterministic scripts (recommended)

> Goal: move routing + validation + assembly into Python; keep the LLM focused on narrow text-to-structure and constrained rewriting.

1. `execution/extract_features.py`

* **Input:** `public_data.json`
* **Output:** `features.json`
* **Job:** keyword + signal extraction (hiring/process/speed/tools/founder/risk). No LLM.

2. `execution/select_codes.py`

* **Input:** `features.json` (+ optional `llm_classification.json`)
* **Output:** `final_classification.json`
* **Job:** deterministic A/B selection, tie-breakers, confidence adjustments, `needs_review`.

3. `execution/select_matrix_cell.py`

* **Input:** `final_classification.json`, `matrix.json`
* **Output:** `selected_cell.json`
* **Job:** deterministic cell selection; nearest-neighbor fallback mapping; logs fallback usage.

4. `execution/compose_email_from_template.py`

* **Input:** `final_classification.json`, `selected_cell.json`
* **Output:** `email_1.json`..`email_4.json`
* **Job:** deterministic assembly using templates (Jinja2 or equivalent). Optional LLM call ONLY for subject variants or light rewrites within constraints.

5. `execution/validate_email.py`

* **Input:** `email_*.json`
* **Output:** `validation_report.json` (pass/fail + reasons + auto-fixes)
* **Job:** schema validation, forbidden words, word-count, line breaks, no bullets, tool-name rules, tone heuristics, etc.

6. `execution/export_to_sheets.py`

* **Input:** final validated outputs
* **Output:** Google Sheet rows

Environment variables, API keys, OAuth tokens live in `.env` and are never hardcoded.

---

## 4) Orchestration Flow (Layer 2)

> Layer 2 should not implement business logic. It should call scripts in order and handle exceptions.

### Step 1 — Validate Inputs

* Confirm required fields exist.
* If `public_data` is thin: proceed, but expect low confidence and `needs_review=true`.

### Step 2 — Feature Extraction (Python)

* Run `execution/extract_features.py`.

### Step 3 — Classification (Hybrid)

* Option A (preferred reliability):

  * Python proposes top A/B candidates from `features.json`.
  * LLM selects among candidates + writes `public_context_sentence` + evidence.
  * Python finalizes via `execution/select_codes.py`.
* Option B (LLM-first, then Python):

  * LLM outputs A/B + evidence.
  * Python validates/corrects via `execution/select_codes.py`.

### Step 4 — Select Matrix Cell (Python)

* Run `execution/select_matrix_cell.py`.
* If fallback used: lower confidence and set `needs_review=true`.

### Step 5 — Compose Emails (Python-first)

* Run `execution/compose_email_from_template.py`.
* LLM use is optional and must be narrow (e.g., subject options) and then validated.

### Step 6 — Quality Gate (Python)

* Run `execution/validate_email.py`.
* If fail: only rewrite the failing part (shorten, remove forbidden terms) and re-validate.

### Step 7 — Export / Deliver

* Export to Sheets/CRM.
* Include columns: lead identifiers, A/B, confidence, evidence, selected_cell, fallback_used, subjects/bodies.

---

## 5) Tie-Breakers (Classification)

* If construction/trades/agency/consulting and projects are mentioned → lean A1.

* If “monthly,” “ongoing,” “managed,” “retainer,” “subscription” → lean A2.

* If HIPAA, patient, legal counsel, compliance, financial advising → lean A3.

* If dispatch, field teams, scheduling, multi-location, inventory → lean A4.

* If heavy outbound/SDR/pipeline/quota language → lean A5.

* If advisory/analysis/writing-heavy deliverables → lean A6.

* If hiring/new roles → B1.

* If SOP/process/systemization → B2.

* If speed/turnaround/efficiency → B3.

* If many tools/integrations/stack → B4.

* If founder is central hub → B5.

* If security/compliance/risk language → B6.

---

## 6) Edge Cases

### 6.1 Low Evidence / Sparse Public Data

* Set `needs_review=true`.
* Use conservative language.
* Keep context sentence factual and generic (industry/service line only).

### 6.2 Prospect Publicly Mentions AI Tools

* Include tool names ONLY if prospect/company publicly referenced them.
* Otherwise use “AI tools” generically.

### 6.3 Regulated Industries

* Avoid implying sensitive details.
* Keep language about “confidential/sensitive data” at a business level.

### 6.4 Missing Matrix Cell

* Python selects nearest neighbor cell.
* Lower confidence.
* Log fallback usage to `.tmp/outbound/run_log.json`.

---

## 7) Self-Annealing Loop

When errors occur:

1. Read the error + stack trace
2. Fix the execution script
3. Test on a single lead
4. Update this directive with the new constraint/flow

Do NOT create or overwrite directives unless explicitly instructed.

---

## 8) Brand Tone (Non-Negotiable)

NeXNet is:

* direct
* calmly confident
* practical
* owner-to-owner
* no fluff, no jargon

If it sounds like generic MSP marketing, it’s wrong.

---

## 9) Definition of Done

* `final_classification.json` exists with evidence + confidence.
* Email #1–#4 JSON outputs exist and pass validation.
* Deliverables exported to a user-accessible surface (Sheets/CRM).
* Intermediates stored in `.tmp/` and can be regenerated.

```

---

## Next build-outs (optional)

- Reply-handling prompts (Yes / Not now / Who are you / Send details)
- The forwarded Shadow AI Audit email + employee intake form copy
- The report template prompt (summary + risks + opportunities)


When errors occur:
1) Read the error + stack trace
2) Fix the execution script
3) Test on a single lead
4) Update this directive with the new constraint/flow

Do NOT create or overwrite directives unless explicitly instructed.

---

## 8) Brand Tone (Non-Negotiable)
NeXNet is:
- direct
- calmly confident
- practical
- owner-to-owner
- no fluff, no jargon

If it sounds like generic MSP marketing, it’s wrong.

---

## 9) Definition of Done
- A/B classification JSON exists with evidence.
- Email #1–#4 JSON outputs exist and pass quality gate.
- Deliverables are exported to a user-accessible surface (Sheets/CRM).
- Intermediates are stored in `.tmp/` and can be regenerated.

```

---

## Next build-outs (optional)

* Reply-handling prompts (Yes / Not now / Who are you / Send details)
* The forwarded Shadow AI Audit email + employee intake form copy
* The report template prompt (summary + risks + opportunities)
