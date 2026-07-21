# NeXNet — Lead Scoring Rules (Cold Email)

**Purpose**  
Define the **enrichment, evaluation, and scoring logic** used *after* the initial scrape to decide which leads are suitable for cold email outreach.

These rules answer **one question only**:

> **“Will this company recognize themselves in our cold email without us having to explain value?”**

---

## Boundary: Enrichment & Scoring Only (Non‑Negotiable)

**This document governs enrichment and scoring only.**

All inputs to this process must:
- Have already passed the *Initial Lead Scrape Rules (Targeting Only)*
- Contain only **raw, non‑enriched data** at ingest

All interpretation, inference, validation, and analysis happens **here — and only here**.

---

## Tier 1 Definition (Cold Email)

> **An owner‑led, document‑heavy firm where control, access, and accountability quietly degrade as the team scales.**

---

## 1. Founder‑Scaled Signals (Scoring Inputs)

The following signals indicate **normalized but felt operational friction**.

Each detected signal contributes to the lead’s total score:

- Founder listed as:
  - CEO
  - Managing Partner
  - Principal
- No internal IT staff listed
- Admin or operations roles handle:
  - IT
  - Systems
  - Onboarding
- Document‑centric language present:
  - Client files
  - Records
  - Case files
  - Plans / reports
- Confidentiality or compliance language present

---

## 2. Scoring Model

A lead is considered **Tier 1 for cold email** if its total score is **6 or higher**.

| Signal | Points |
|------|------|
| Founder still listed as CEO / Partner | +2 |
| No internal IT role | +2 |
| Document‑heavy services | +1 |
| Compliance / confidentiality language | +1 |
| Admin / ops handles IT | +1 |
| 15+ employees | +1 |

### Tier Handling

| Tier | Score | Enrichment | Outreach |
|------|-------|------------|----------|
| **Tier 1** | ≥ 6 | Yes — full enrichment | Personalized cold email sequence |
| **Tier 2** | < 6 | No — skip enrichment | Nurture / future outreach |

> **Note:** Tier 2 leads are **not discarded**. They are uploaded to the sheet without enrichment for potential future outreach or nurture campaigns.

---

## 3. Hard Disqualifiers (Kill Switch)

If **any** of the following are detected during scoring, the lead is discarded regardless of score:

- In‑house IT staff or MSP explicitly listed
- Founder acting as CTO or IT Director
- Private equity ownership or roll‑up language
- Fewer than 5 employees

---

## 4. Output Requirements (Mandatory)

For a lead to be approved for outreach, the scoring process must produce:

- Company name
- Website URL
- Vertical
- Estimated employee count
- Founder name and title
- Detected founder‑scaled signals (list)
- Total score with signal‑level breakdown
- **Recommended outreach angle:** Shadow AI & Access Audit

If this information cannot be populated reliably, the lead is **not approved**.

---

## 5. Post‑Score Enrichment (Tier 1 Only)

> **Critical.** Leads scoring 6+ require enrichment *before* handoff to the cold email generator.  
> Without enrichment, the public context sentence will be generic and ineffective.

### Purpose

Collect **public, observable signals** that enable the cold email generator to write a single, specific public context sentence such as:

- "Saw your post about cutting inefficiencies."
- "Noticed you're hiring for operations — looks like the team's scaling."
- "Was reading about how you handle client deliverables."

### Required Data Sources (Collect All Available)

| Source | What to Collect | Field Name |
|--------|-----------------|------------|
| **Founder LinkedIn** | 3–5 most recent posts/activity | `founder_linkedin_posts` |
| **Company LinkedIn** | 3–5 most recent company page posts | `company_linkedin_posts` |
| **Company Website** | Services page text, About page text, recent blog headlines/snippets | `website_snippets` |

### Enrichment Rules

1. **Trigger**: Enrichment runs **only** for leads with `lead_score >= 6` (Tier 1).
2. **Best Effort**: If a source is unavailable (e.g., no LinkedIn activity), continue with available sources.
3. **Minimum Viable**: At least ONE source must yield usable content. If all three fail, flag the lead as `enrichment_failed`.
4. **No Fabrication**: Do not infer or generate content. Store only what is publicly visible.
5. **Recency Preference**: Prioritize content from the last 6 months.

### Output Fields (Added to Lead Record)

```json
{
  "founder_linkedin_posts": ["Post 1 text...", "Post 2 text..."],
  "company_linkedin_posts": ["Post 1 text...", "Post 2 text..."],
  "website_snippets": {
    "services": "We specialize in complex commercial builds...",
    "about": "Founded in 2012, our team of 25...",
    "blog_headlines": ["How We Reduced Project Delays by 30%", "..."]
  },
  "enrichment_status": "complete" | "partial" | "failed",
  "enrichment_sources": ["founder_linkedin", "company_website"]
}
```

### Handoff to Cold Email Generator

The cold email generator (`cold_email_generator.py`) must:

1. Check `enrichment_status` before generating emails.
2. Use enriched fields to craft the public context sentence.
3. Fall back to `company_description` only if `enrichment_status == "failed"`.

---

## Notes

- These rules are intentionally strict to eliminate “explaining value” conversations.
- Scoring logic may evolve without changing the initial scrape rules.
- This document is campaign‑specific and should not be reused blindly for other verticals or outreach types.

