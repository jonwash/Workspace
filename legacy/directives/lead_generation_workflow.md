# Lead Generation Workflow Directive

**Goal**: Scrape high-quality leads using Apify (`code_crafter/leads-finder`) that match NeXNet targeting criteria.

## Inputs
1.  **Search Query**: The query to send to Google Maps/search (e.g., "Architecture firms in Chicago").
2.  **Targeting Directive**: `directives/ne_xnet_cold_email_targeting_directive.md` (Defines inclusion/exclusion rules).
3.  **Total Leads**: Desired number of leads (after filtering).

## Process

### Phase 1: Test Run (Validation)
1.  **Sample**: Scrape **25 leads** using the Search Query.
2.  **Verify**: Check leads against Hard Stops in Targeting Directive:
    -   **Industry**: Must be allowed list.
    -   **Employees**: Must be > 10, < 100.
    -   **Email**: Must be business domain (no @gmail, @yahoo).
    -   **Website**: Must exist.
3.  **Decision**:
    -   **If success rate >= 80%**: Proceed to Phase 2.
    -   **If success rate < 80%**: **STOP**. Refine the Search Query or settings. notify user.

### Phase 2: Full Execution
1.  **Scrape**: Run the scraper for the remaining amount (Total Leads - 25).
2.  **Filter**: Apply the same verification logic to the full batch.
3.  **Score**: Apply lead scoring rules. Tag leads as Tier 1 (score ≥ 6) or Tier 2 (score < 6).

> **Note:** Both Tier 1 and Tier 2 leads are retained. Only enrichment is conditional.

### Phase 3: Enrichment (Tier 1 Only)

> **Critical Step.** Without enrichment, cold emails will have generic public context sentences.

For each Tier 1 lead, collect:

1.  **Founder LinkedIn Posts**: Scrape 3–5 most recent posts from the founder's LinkedIn profile.
2.  **Company LinkedIn Posts**: Scrape 3–5 most recent posts from the company's LinkedIn page.
3.  **Company Website/Blog**: Extract text from services page, about page, and recent blog headlines.

**Rules:**
-   Enrichment is **best effort** — continue if one source fails.
-   At least one source must succeed, or flag lead as `enrichment_failed`.
-   Store raw text; LLM will synthesize during email generation.

**See:** `directives/ne_xnet_lead_scoring_rules_cold_email.md` Section 5 for detailed enrichment rules.

### Phase 4: Upload
1.  **Upload**: Add **all qualified leads** (Tier 1 and Tier 2) to the designated Google Sheet.
2.  **Tier 1 Leads**: Include all enrichment fields (`founder_linkedin_posts`, `company_linkedin_posts`, `website_snippets`, `enrichment_status`).
3.  **Tier 2 Leads**: Upload with basic fields only (no enrichment). Set `enrichment_status = "skipped"` and leave enrichment fields empty.

## Tools
-   **Execution Script**: `execution/lead_gen_orchestrator.py`
-   **Enrichment Script**: `execution/lead_enricher.py` *(new)*
-   **Apify Actor**: `code_crafter/leads-finder`
-   **LinkedIn Scraper**: Apify `apify/linkedin-profile-scraper` or equivalent
-   **Website Scraper**: `requests` + `BeautifulSoup` (built-in)

## Outputs
-   A Google Sheet populated with **all qualified leads** (Tier 1 enriched, Tier 2 basic).
-   Enrichment fields populated for Tier 1 leads (for personalized cold email).
-   Tier 2 leads included for nurture/future outreach.
-   A summary report of the run (Total found, Tier 1, Tier 2, Enriched, Enrichment Failed).
