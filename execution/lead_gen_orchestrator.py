import os
import sys
import argparse
import json
from time import sleep

# Import local modules
try:
    from apify_scraper import run_scraper
    from gcal_sheets import upload_leads
    from lead_scoring import score_lead
    from lead_enricher import enrich_lead, mark_tier2_skipped
except ImportError as e:
    # If running from root, adjust path or assume execution package
    try:
        from execution.apify_scraper import run_scraper
        from execution.gcal_sheets import upload_leads
        from execution.lead_scoring import score_lead
        from execution.lead_enricher import enrich_lead, mark_tier2_skipped
    except ImportError:
         print(f"Import Error: {e}")
         print("Make sure you are running this from the workspace root or execution directory.")
         pass

def check_criteria(lead):
    """
    Verify if a lead matches NeXNet criteria.
    Returns: (bool, reason)
    """
    # Normalize fields (map G-Maps to standard)
    lead['company_name'] = lead.get('title') or lead.get('company_name')
    lead['website'] = lead.get('website') or lead.get('company_website')
    lead['address'] = lead.get('address') or lead.get('company_full_address')

    # 1. Business Check (Email OR Website OR Phone)
    email = lead.get('email', '')
    website = lead.get('website', '')
    
    # Strict email check removed for G-Maps scraping as it usually doesn't return emails.
    # We accept if there is a website or a valid business name/address.
    
    if not email and not website:
         # Some G-Maps leads have neither, but might have phone/address. 
         # We want high quality, so require at least website OR business email.
         return False, "No email or website"
    
    if email:
        free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        if any(domain in email for domain in free_domains):
            # If ONLY personal email and NO website, maybe reject? 
            # For now, flag it but allow if website exists.
            if not website:
                return False, "Personal email only"

    return True, "Passed"

def check_competitors(lead):
    """
    Check if the lead is a competitor (IT/MSP).
    Returns: (bool, reason) - True if competitor, False otherwise.
    """
    poison_keywords = [
        "it services", "managed services", "network security", 
        "computer consulting", "msp", "cloud computing",
        "cyber security", "tech support", "information technology",
        "software development", "web development", "digital agency"
    ]
    
    # Combine relevant fields for scanning
    text_to_scan = (
        f"{lead.get('keywords', '')} "
        f"{lead.get('company_description', '')} "
        f"{lead.get('headline', '')} "
        f"{lead.get('company_name', '')}"
    ).lower()
    
    found_poison = [pk for pk in poison_keywords if pk in text_to_scan]
    
    if found_poison:
        return True, f"Competitor detected: {found_poison[0]}"
        
    return False, "Not a competitor"

def load_config():
    """Load configuration from .env or environment variables."""
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle "KEY=value" or "KEY='value'"
                    if '=' in line:
                        k, v = line.split('=', 1)
                        if k not in os.environ:
                            # simple unquote
                            v = v.strip("'").strip('"')
                            os.environ[k] = v

def main():
    load_config()
    parser = argparse.ArgumentParser(description="NeXNet Lead Generation Orchestrator")
    parser.add_argument("--query", required=True, help="Search query for Google Maps/Apify")
    parser.add_argument("--total", type=int, default=50, help="Total qualified leads desired")
    parser.add_argument("--sheet-id", help="Google Sheet ID to upload to (optional, will create new if missing)")
    parser.add_argument("--share-email", help="Email to share the new sheet with")
    parser.add_argument("--test-only", action="store_true", help="Run only the test phase (25 leads)")
    
    args = parser.parse_args()
    
    apify_token = os.environ.get("APIFY_TOKEN")
    if not apify_token:
        print("Error: APIFY_TOKEN environment variable not set.")
        sys.exit(1)

    # Defaults
    share_email = args.share_email or os.environ.get("SHARE_EMAIL")

    # PHASE 1: TEST RUN/SMALL RUN
    # Adjust initial fetch based on total request to avoid over-scraping
    if args.total < 25:
        # Fetch EXACTLY the requested amount. No buffer.
        initial_fetch = args.total
        print(f"--- Phase 1: Small Run (Fetching {initial_fetch} leads) ---")
    else:
        # For large batches, start with standard test size
        initial_fetch = 25
        print("--- Phase 1: Test Run (25 leads) ---")
    
    # Parse query mapping (Hardcoded for "Accounting in Raleigh")
    # In a real app, use an arg or simple keyword matching
    city = "Raleigh" if "Raleigh" in args.query else ""
    state = "North Carolina" if "NC" in args.query or "North Carolina" in args.query else ""
    industry = "Accounting" if "Accounting" in args.query else []
    
    # Default filters based on Directive
    input_filters = {
        "fetch_count": initial_fetch,
        "email_status": ["validated"],
        "contact_job_title": ["Owner", "Partner", "Principal", "CEO", "Founder", "Managing Partner"],
        # Per docs: Use contact_city instad of Location for city-level targeting. Leave Location empty.
        "contact_location": [],
        "contact_city": ["Raleigh"],
        "company_industry": [industry.lower()] if industry else [],
        "company_not_industry": ["restaurants", "retail"],
        # Filter size based on Workflow (< 100)
        "size": ["11-20", "21-50", "51-100"],
    }
    
    # Fallback if parsing failed
    if not city and not industry:
        print("Warning: Could not parse City/Industry from query. Using defaults or raw query may fail.")
    
    try:
        test_leads = run_scraper(input_filters, apify_token)
    except Exception as e:
        print(f"Scraping failed: {e}")
        sys.exit(1)
    
    qualified_test = []  # Tier 1 leads (will be enriched)
    tier2_leads = []      # Tier 2 leads (skipped enrichment, kept for nurture)
    valid_leads_count = 0

    for lead in test_leads:
        is_valid, reason = check_criteria(lead)
        if is_valid:
            valid_leads_count += 1
            
            # Secondary Check: Competitors
            is_competitor, comp_reason = check_competitors(lead)
            if is_competitor:
                # print(f"Skipping Competitor: {lead.get('company_name')} ({comp_reason})")
                continue
            
            # SCORING
            lead = score_lead(lead)
            print(f"  > Scored: {lead.get('lead_score')} pts ({lead.get('tier')})")
            
            # Separate by tier (both are kept)
            if lead.get('lead_score') >= 6:
                qualified_test.append(lead)
            else:
                # Mark Tier 2 as skipped for enrichment
                lead = mark_tier2_skipped(lead)
                tier2_leads.append(lead)
    
    validity_rate = valid_leads_count / len(test_leads) if test_leads else 0
    yield_rate = len(qualified_test) / len(test_leads) if test_leads else 0
    
    print(f"Test Run Results:")
    print(f"  - Search Validity: {validity_rate:.1%} (Threshold 80%)")
    print(f"  - Final Yield:     {yield_rate:.1%} (Informational)")
    
    if validity_rate < 0.8:
        print(f"FAILURE: Search Validity ({validity_rate:.1%}) < 80%.")
        print("The search query is returning too many invalid results (missing email/website).")
        print("Please refine your Search Query or targeting parameters.")
        sys.exit(1)
        
    print(f"Success: Validity Passed. Proceeding...")
    
    if args.test_only:
        return

    # PHASE 2: FULL RUN
    remaining_needed = args.total - len(qualified_test)
    if remaining_needed > 0:
        # Fetch EXACTLY what is missing. No buffer.
        scrape_count = remaining_needed
        print(f"--- Phase 2: Full Run (Scraping {scrape_count} more) ---")
        
        # Update limit in filters
        input_filters["fetch_count"] = scrape_count
        
        try:
            more_leads = run_scraper(input_filters, apify_token)
            for lead in more_leads:
                is_valid, reason = check_criteria(lead)
                if is_valid:
                    # Secondary Check: Competitors
                    is_competitor, comp_reason = check_competitors(lead)
                    if is_competitor:
                        continue

                    # SCORING
                    lead = score_lead(lead)
                    
                    # Separate by tier (both are kept)
                    if lead.get('lead_score') >= 6:
                        qualified_test.append(lead)
                        if len(qualified_test) >= args.total:
                            break
                    else:
                        # Mark Tier 2 as skipped for enrichment
                        lead = mark_tier2_skipped(lead)
                        tier2_leads.append(lead)
        except Exception as e:
            print(f"Scraping continued failed: {e}")

    print(f"Total Tier 1 leads collected: {len(qualified_test)}")
    print(f"Total Tier 2 leads collected: {len(tier2_leads)}")
    
    # PHASE 3: ENRICHMENT (Tier 1 only)
    print(f"--- Phase 3: Enrichment (Tier 1 leads) ---")
    enriched_count = 0
    failed_count = 0
    
    for i, lead in enumerate(qualified_test):
        print(f"  Enriching [{i+1}/{len(qualified_test)}]: {lead.get('company_name')}...")
        try:
            lead = enrich_lead(lead)
            status = lead.get('enrichment_status', 'unknown')
            sources = lead.get('enrichment_sources', [])
            print(f"    > Status: {status} | Sources: {', '.join(sources) if sources else 'none'}")
            
            if status in ['complete', 'partial']:
                enriched_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"    > Enrichment failed: {e}")
            lead['enrichment_status'] = 'failed'
            lead['enrichment_sources'] = []
            failed_count += 1
    
    print(f"Enrichment complete: {enriched_count} succeeded, {failed_count} failed")
    
    # PHASE 4: UPLOAD (all leads)
    # Combine Tier 1 (enriched) and Tier 2 (skipped) leads
    all_leads = qualified_test + tier2_leads
    
    # Trim to requested total if needed
    leads_to_upload = all_leads[:args.total + len(tier2_leads)]  # Keep all tier 2 for nurture
    
    print(f"--- Phase 4: Upload ---")
    print(f"Uploading {len(qualified_test)} Tier 1 + {len(tier2_leads)} Tier 2 = {len(leads_to_upload)} total leads...")
    
    try:
        # Call module
        sheet_url = upload_leads(leads_to_upload, args.sheet_id, share_email, args.query, industry=industry, location=city)
        print(f"View your leads here: {sheet_url}")
    except Exception as e:
        print(f"Error uploading to Sheets: {e}")
        filename = os.path.join(".tmp", "qualified_leads.json")
        os.makedirs(".tmp", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(all_leads, f, indent=2, default=str)
        print(f"Leads saved to {filename}")

if __name__ == "__main__":
    main()
