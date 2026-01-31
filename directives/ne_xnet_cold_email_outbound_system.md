# Cold Email Creation Directive — NeXNet

> **Single‑purpose directive.** This file defines *only* how NeXNet generates a 4‑email cold outreach sequence.
> It is intentionally concise and mirrored across `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.

---

## 1) Purpose
Generate a **4‑email cold outbound sequence** that is:
- deeply personalized via **defensible inference**
- repeatable and reliable at scale
- non‑creepy and non‑accusatory
- aligned with NeXNet’s tone: *direct, calm, owner‑to‑owner, no fluff*

**Primary mini‑offer:** Shadow AI Usage Audit (forwarded internal email).

---

## 2) Inputs (per lead)
- `lead_id`
- `first_name`
- `company_name`
- `role_title`
- **Enrichment Data** (supplied by `lead_enricher.py`):
  - `founder_linkedin_posts` — array of 3–5 recent founder posts
  - `company_linkedin_posts` — array of 3–5 recent company page posts
  - `website_snippets` — object containing `services`, `about`, `blog_headlines`
  - `enrichment_status` — `"complete"`, `"partial"`, or `"failed"`
  - `enrichment_sources` — list of sources that yielded data
- **Deep Personalization Matrix (JSON)**

Leads are read from an **existing Google Sheet** owned by the lead‑gen workflow.

> **Note:** If `enrichment_status == "failed"`, fall back to `company_description` for the public context sentence.

---

## 3) Outputs (per lead)
- A/B classification + confidence + evidence
- Public context sentence
- Email #1–#4 (subjects + bodies)
- Validation status

Outputs are written **back to the same Google Sheet row**, keyed by `lead_id`, **formatted for Instantly ingestion**.

---

## Instantly Integration (Delivery Platform)

> Instantly is the outbound delivery system. This directive governs **copy generation only**, but output must conform to Instantly constraints.

### Instantly Formatting Rules (Non-Negotiable)
- Plain text only (no HTML, no Markdown)
- Subject and body stored in separate fields
- No variables beyond Instantly-supported placeholders (e.g., `{{first_name}}`, `{{company}}` if used)
- Line breaks must be intentional and minimal (≤2 in Email #1)
- No links in Email #1 unless explicitly approved later

### Sequence Mapping
- Email #1 → Instantly Step 1
- Email #2 → Instantly Step 2
- Email #3 → Instantly Step 3
- Email #4 → Instantly Step 4

### Write-Back Expectations
- Each email’s subject/body must map cleanly to Instantly columns or payload fields
- Copy must be immediately send-ready (no placeholders requiring manual cleanup)

---

## 4) High‑Level Flow (3‑Layer Model)

### Step 0 — Eligibility Check (Gate)

> **Critical.** Cold emails are only generated for leads that meet both criteria below.

| Check | Condition | If Fails |
|-------|-----------|----------|
| **Tier** | `tier == "Tier 1"` | Skip — Tier 2 leads are for nurture only |
| **Enrichment** | `enrichment_status in ["complete", "partial"]` | Skip — insufficient personalization data |

If either check fails, the lead is **skipped** and the generator moves to the next row. The `Email 1 Body` field remains empty.

### Step 1 — Feature Extraction (Execution)
Extract deterministic signals from public text (e.g., hiring, speed, tools, founder‑centricity, risk/compliance).

### Step 2 — Classification (Hybrid)
Select **ONE** Business Model code (A1–A6) and **ONE** Execution Pressure code (B1–B6).
Produce:
- A‑code, B‑code
- confidence score
- 2–4 evidence bullets
- **one public context sentence** (public facts only)

### Step 3 — Matrix Selection (Execution)
Select the inference paragraph for `{A}_{B}`.
If missing, apply nearest‑neighbor fallback and lower confidence.

### Step 4 — Compose Emails #1–#4 (Structure‑Enforced)
Assemble emails using the fixed structures in Section 5.
Personalization is allowed **only** via:
- public context sentence
- selected inference paragraph

### Step 5 — Validation (Execution)
Enforce word counts, structure, forbidden language, and tone.
If invalid, revise only the failing portion and re‑validate.

### Step 6 — Write Back to Sheet
Write outputs to the existing lead‑gen Google Sheet.
Never overwrite human copy unless `regenerate=true`.

---

## 5) Public Context Sentence (Required)

The **public context sentence** is the *only* factual personalization in the email. It anchors the message in reality and gives permission for the inference that follows.

### What it is
- A **single sentence** (1–2 short clauses)
- Based **only on publicly visible information**
- Describes *what the company is doing*, not what it is thinking or experiencing

### What it is NOT
- Not an assumption
- Not a diagnosis
- Not a compliment
- Not a summary of their entire business

### Rules
- Must be defensibly true from public sources
- Must not reference private behavior or internal tools
- Must not imply research depth (no “I spent time analyzing…”)
- Must stand alone without inference or opinion

### Acceptable Sources
- Company website (services, positioning, industries served)
- Founder LinkedIn headline/about section
- Recent public posts or announcements
- Job listings or hiring pages

### Examples (Good)
- “I saw that your team focuses on remodel projects with tight delivery timelines.”
- “Noticed your firm works closely with clients on ongoing advisory engagements.”
- “Saw you’re hiring for operations as the team continues to grow.”
- “From your site, it looks like your team handles sensitive client information day to day.”

### Examples (Bad)
- “I know your team is moving fast internally.”
- “It seems like your tech stack is getting complex.”
- “You’re probably using a lot of AI already.”
- “I spent some time digging into how your team works.”

---

## 6) Email Structure (Non-Negotiable) (Non‑Negotiable)

### Email #1 — Initial Outreach
**Purpose:** Establish relevance through insight.

**Required order:**
1. Subject (short, natural)
2. Greeting
3. Public context sentence
4. One inference paragraph (from matrix)
5. Shadow AI Audit offer (visibility‑first framing)
6. Yes/No CTA
7. Signature

**Rules:**
- 80–140 words
- ≤2 line breaks
- No bullets
- No AI tool names unless prospect publicly mentioned them

---

### Email #2 — Normalization Follow‑Up
**Purpose:** Reduce friction and defensiveness.

**Required elements:**
- brief follow‑up
- normalization (“this is common”)
- visibility framing (not control)
- yes/no CTA

**Rules:** ≤90 words; no new personalization.

---

### Email #3 — Insight Reinforcement
**Purpose:** Build credibility without fear.

**Required elements:**
- 2–3 anonymized patterns owners typically discover
- opportunity‑focused framing
- invitation to review internally

**Rules:** ≤110 words; no client names or private statistics.

---

### Email #4 — Clean Exit
**Purpose:** Close the loop respectfully.

**Required elements:**
- acknowledge timing
- one‑sentence audit restatement
- permission to disengage

**Rules:** ≤70 words; no pressure language.

---

## 6) Guardrails
- Do not claim certainty about private behavior.
- Do not introduce new facts to sound personalized.
- No MSP clichés or fear‑based language.
- CTA is always a simple yes/no.

---

## 7) Definition of Done
- A/B classification exists with evidence + confidence.
- Emails #1–#4 pass validation.
- Outputs written back to the lead‑gen Google Sheet.
- Intermediates are disposable and fully regenerable.

