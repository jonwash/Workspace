# Lead Enrichment Implementation Plan

**Created:** 2026-01-15  
**Status:** In Progress (Phase 1 Complete)  
**Objective:** Enable personalized "public context sentences" in cold emails by enriching Tier 1 leads with publicly observable signals from LinkedIn and company websites.

---

## Executive Summary

The cold email system currently generates generic public context sentences because the upstream workflow does not collect the personalization data the directive requires. This plan adds an **Enrichment Step** between lead scoring and email generation that collects:

1. **Founder LinkedIn Posts** (3–5 recent posts)
2. **Company LinkedIn Posts** (3–5 recent posts)
3. **Company Website Snippets** (services, about, blog headlines)

---

## Problem Statement

### Current State
```
Apify Scrape → Criteria Check → Competitor Filter → Lead Scoring → Upload to Sheets → Cold Email Generator
```

**Issue:** The `cold_email_generator.py` receives only `company_description` and `keywords` — which are often thin or missing. The fallback is:
```python
context = f"Noticed you are active in the {lead.get('company_industry', 'industry')} space."
```

### Target State
```
Apify Scrape → Criteria Check → Competitor Filter → Lead Scoring 
    ├─→ (Tier 1) Enrichment → Upload to Sheets → Cold Email Generator
    └─→ (Tier 2) Skip Enrichment → Upload to Sheets (for nurture)
```

**Result:** 
- **Tier 1 leads** receive structured enrichment data enabling context sentences like:
  - "Saw your post about cutting inefficiencies."
  - "Noticed you're hiring for operations — looks like the team's scaling."
- **Tier 2 leads** are retained for nurture/future outreach (no enrichment cost).

---

## Data Sources & Collection Strategy

### 1. Founder LinkedIn Posts

| Attribute | Value |
|-----------|-------|
| **Source** | LinkedIn personal profile (posts/activity feed) |
| **Data Needed** | 3–5 most recent posts (text only) |
| **Frequency** | Once per lead (at enrichment time) |
| **Input Required** | Founder's LinkedIn profile URL or `first_name + last_name + company` |

**Collection Options:**

| Option | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **Apify `apify/linkedin-profile-scraper`** | Reliable, scales, handles auth | Cost per run (~$0.05/profile) | ✅ Primary |
| **Apify `curious_coder/linkedin-post-search`** | Direct post scraping | May need profile URL first | Backup |
| **RapidAPI `linkedin-api`** | Real-time, official-ish | Rate limits, auth complexity | ❌ |
| **Manual (MVP)** | Free | Doesn't scale | ❌ |

**Recommended Actor:** `apify/linkedin-profile-scraper` with posts extraction enabled.

---

### 2. Company LinkedIn Posts

| Attribute | Value |
|-----------|-------|
| **Source** | LinkedIn company page (posts feed) |
| **Data Needed** | 3–5 most recent company posts (text only) |
| **Frequency** | Once per lead (at enrichment time) |
| **Input Required** | Company LinkedIn URL or company name |

**Collection Options:**

| Option | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **Apify `apify/linkedin-company-scraper`** | Reliable, includes posts | Cost per run | ✅ Primary |
| **Apify `curious_coder/linkedin-company-posts`** | Post-focused | Newer, less tested | Backup |

**Recommended Actor:** `apify/linkedin-company-scraper` (often bundled with profile scraper credits).

---

### 3. Company Website/Blog

| Attribute | Value |
|-----------|-------|
| **Source** | Company website (services, about, blog pages) |
| **Data Needed** | Services page text, About page text, 3–5 blog headlines |
| **Frequency** | Once per lead (at enrichment time) |
| **Input Required** | Company website URL |

**Collection Options:**

| Option | Pros | Cons | Recommended |
|--------|------|------|-------------|
| **`requests` + `BeautifulSoup`** | Free, fast, built-in | Fails on JS-rendered sites | ✅ Primary |
| **Apify `apify/web-scraper`** | Handles JS, headless | Overkill for simple pages | Backup |
| **Playwright/Puppeteer** | Full JS rendering | Heavier, slower | ❌ |

**Recommended Approach:** `requests` + `BeautifulSoup` with smart URL discovery for `/about`, `/services`, `/blog`.

---

## Data Model

### Enriched Lead Record (Additional Fields)

```python
{
    # ... existing lead fields ...
    
    # NEW: Enrichment Fields
    "founder_linkedin_url": "https://linkedin.com/in/john-smith",
    "founder_linkedin_posts": [
        "Just wrapped our biggest project yet. Team crushed it.",
        "Hiring two ops coordinators — we're scaling faster than expected.",
        "Fighting tool sprawl this quarter. Too many apps, not enough process."
    ],
    
    "company_linkedin_url": "https://linkedin.com/company/acme-builders",
    "company_linkedin_posts": [
        "Proud to announce our new office location in downtown Raleigh!",
        "Our team just completed a complex commercial build ahead of schedule.",
        "We're hiring! Looking for project managers who thrive under pressure."
    ],
    
    "website_snippets": {
        "services": "We specialize in commercial construction, tenant improvements, and design-build projects across the Triangle region.",
        "about": "Founded in 2015, Acme Builders is a family-owned general contractor with 28 employees focused on quality and client relationships.",
        "blog_headlines": [
            "How We Reduced Project Delays by 30%",
            "Why We Invested in Project Management Software",
            "Client Spotlight: Downtown Office Renovation"
        ]
    },
    
    "enrichment_status": "complete",  # "complete" | "partial" | "failed"
    "enrichment_sources": ["founder_linkedin", "company_linkedin", "website"],
    "enrichment_timestamp": "2026-01-15T19:30:00Z"
}
```

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     lead_gen_orchestrator.py                        │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────────┐ │
│  │ Apify Scrape│ → │ Lead Scoring │ → │ Tier Check                │ │
│  └─────────────┘   └──────────────┘   └───────────────────────────┘ │
│                                          │                          │
│                               ┌──────────┴──────────┐               │
│                               ↓                     ↓               │
│                     ┌─────────────────┐   ┌─────────────────┐       │
│                     │ Tier 1: Enrich  │   │ Tier 2: Skip    │       │
│                     └─────────────────┘   └─────────────────┘       │
│                               │                     │               │
│                               └──────────┬──────────┘               │
│                                          ↓                          │
│                              ┌─────────────────────────┐            │
│                              │ Upload ALL to Sheets    │            │
│                              └─────────────────────────┘            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      lead_enricher.py (NEW)                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      enrich_lead(lead)                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│       ↓                    ↓                      ↓                 │
│  ┌──────────┐      ┌───────────────┐      ┌──────────────────┐      │
│  │ LinkedIn │      │ Company       │      │ Website          │      │
│  │ Founder  │      │ LinkedIn      │      │ Scraper          │      │
│  │ Scraper  │      │ Scraper       │      │ (BeautifulSoup)  │      │
│  └──────────┘      └───────────────┘      └──────────────────┘      │
│       ↓                    ↓                      ↓                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 Merge → Return Enriched Lead                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Changes Required

### New Files

| File | Purpose |
|------|---------|
| `execution/lead_enricher.py` | Main enrichment module with `enrich_lead()` function |
| `execution/linkedin_scraper.py` | LinkedIn-specific scraping via Apify actors |
| `execution/website_scraper.py` | Website text extraction via BeautifulSoup |

### Modified Files

| File | Changes |
|------|---------|
| `execution/lead_gen_orchestrator.py` | Call `enrich_lead()` after scoring, before upload |
| `execution/cold_email_generator.py` | Update `generate_public_context()` to use enrichment fields |
| `execution/gcal_sheets.py` | Add columns for enrichment fields during upload |
| `.env` | Add `APIFY_LINKEDIN_TOKEN` if separate from main token |

---

## Implementation Phases

### Phase 1: Website Scraper (Low-Hanging Fruit)
**Timeline:** 1–2 hours  
**Risk:** Low

1. Create `execution/website_scraper.py`
   - `scrape_website(url)` → returns `{ services, about, blog_headlines }`
   - Use `requests` + `BeautifulSoup`
   - Smart URL discovery: try `/about`, `/about-us`, `/services`, `/blog`
   - Handle 404s, timeouts gracefully

2. Create basic `execution/lead_enricher.py`
   - `enrich_lead(lead)` → calls website scraper
   - Set `enrichment_status` based on success

3. Integrate into `lead_gen_orchestrator.py`
   - Call enricher after scoring **for Tier 1 leads only**
   - Set `enrichment_status = "skipped"` for Tier 2 leads
   - Upload **all qualified leads** (both tiers)

**Deliverable:** Website snippets in Tier 1 lead records; Tier 2 leads flow through unchanged

---

### Phase 2: LinkedIn Scraper Integration
**Timeline:** 2–3 hours  
**Risk:** Medium (API costs, rate limits)

1. Create `execution/linkedin_scraper.py`
   - `scrape_founder_linkedin(url_or_name, company, apify_token)`
   - `scrape_company_linkedin(url_or_name, apify_token)`
   - Use Apify actors via REST API

2. Expand `execution/lead_enricher.py`
   - Add LinkedIn scraping to `enrich_lead()`
   - Parallel scraping if possible (concurrent futures)

3. Handle LinkedIn URL discovery
   - If `founder_linkedin_url` not in lead, search by name + company
   - If `company_linkedin_url` not in lead, search by company name

**Deliverable:** Full enrichment (website + LinkedIn)

---

### Phase 3: Cold Email Generator Update
**Timeline:** 1–2 hours  
**Risk:** Low

1. **Add Eligibility Gate** in `main()` loop (before processing)
   ```python
   # Skip Tier 2 leads
   if lead.get('tier') != 'Tier 1':
       print(f"  > Skipping {lead.get('company_name')} (Tier 2 - nurture only)")
       continue
       
   # Skip leads without enrichment
   enrichment_status = lead.get('enrichment_status', '')
   if enrichment_status not in ['complete', 'partial']:
       print(f"  > Skipping {lead.get('company_name')} (enrichment: {enrichment_status})")
       continue
   ```

2. Update `generate_public_context()` in `cold_email_generator.py`
   - Check `enrichment_status`
   - Use `founder_linkedin_posts` first (most personal)
   - Fall back to `company_linkedin_posts`
   - Fall back to `website_snippets`
   - Fall back to `company_description` (current behavior — only if enrichment failed)

3. Update the LLM prompt
   - Pass enrichment data to the prompt
   - Instruct model to reference specific posts/content

**Deliverable:** 
- Eligibility gate prevents wasted LLM calls on Tier 2/unenriched leads
- Personalized public context sentences for qualified leads

---

### Phase 4: Testing & Validation
**Timeline:** 1 hour  
**Risk:** Low

1. Test enrichment with 5 known leads
   - Verify data quality from each source
   - Check edge cases (no LinkedIn, broken website)

2. Validate email output quality
   - Generate emails for enriched vs. non-enriched leads
   - Compare personalization quality

3. Monitor costs
   - Track Apify credits usage
   - Optimize if needed (batch, caching)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LinkedIn blocks scraping | Medium | High | Use Apify actors (they handle anti-bot) |
| Apify costs exceed budget | Medium | Medium | Set credit limits, batch efficiently |
| Founder LinkedIn URL missing | High | Medium | Fallback to company LinkedIn + website |
| Website is JS-rendered | Low | Low | Fallback to other sources |
| Rate limiting | Medium | Medium | Add delays, respect robots.txt |

---

## Cost Estimate

| Source | Cost per Lead | Notes |
|--------|---------------|-------|
| Founder LinkedIn (Apify) | ~$0.05 | Per profile scrape |
| Company LinkedIn (Apify) | ~$0.03 | Often cheaper than personal |
| Website (BeautifulSoup) | $0.00 | Built-in, free |
| **Total per lead** | **~$0.08** | |

For 50 leads: **~$4.00** in Apify credits.

---

## Success Metrics

1. **Enrichment Success Rate**: ≥80% of Tier 1 leads have `enrichment_status == "complete" or "partial"`
2. **Personalization Quality**: Cold email context sentences reference specific, verifiable public facts
3. **Cost Efficiency**: Enrichment cost stays under $0.15/lead

---

## Next Steps

1. [x] Approve this implementation plan
2. [x] Implement Phase 1: Website Scraper ✅ **COMPLETE** (2026-01-15)
   - Created `execution/website_scraper.py`
   - Created `execution/lead_enricher.py`  
   - Integrated into `execution/lead_gen_orchestrator.py`
   - Tested successfully
3. [ ] Implement Phase 2: LinkedIn Scraper
4. [ ] Implement Phase 3: Cold Email Generator Update
5. [ ] Run Phase 4: Testing & Validation
6. [ ] Deploy to production workflow

---

## Appendix: Sample LLM Prompt for Updated Public Context

```python
prompt = f"""
You are Jon, the owner of NeXNet, writing a direct, peer-to-peer email.

Task: Write ONE "Public Context Sentence" that proves you looked at their business.

ENRICHMENT DATA (use this first):
- Founder LinkedIn Posts: {founder_posts}
- Company LinkedIn Posts: {company_posts}
- Website Snippets: {website_snippets}

FALLBACK (only if above is empty):
- Company Description: {desc}
- Keywords: {keywords}

STYLE:
- Start with "Saw your post about...", "Noticed you're...", "Was reading about..."
- Reference SPECIFIC content from the enrichment data
- Under 20 words
- No compliments, no fluff

Output (single sentence only):
"""
```
