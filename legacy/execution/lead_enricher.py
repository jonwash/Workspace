"""
Lead Enricher Module

Orchestrates the collection of enrichment data for Tier 1 leads.
Currently supports:
- Website snippets (services, about, blog headlines)

Future additions:
- Founder LinkedIn posts
- Company LinkedIn posts

See: directives/ne_xnet_lead_scoring_rules_cold_email.md Section 5
"""

import os
import sys
from datetime import datetime, timezone

# Import website scraper
try:
    from execution.website_scraper import scrape_website
except ImportError:
    from website_scraper import scrape_website


def enrich_lead(lead):
    """
    Enrich a single lead with public data for personalization.
    
    This function is called ONLY for Tier 1 leads (score >= 6).
    Tier 2 leads should be marked with enrichment_status = "skipped" before this is called.
    
    Args:
        lead (dict): The lead record with at least 'website' field
        
    Returns:
        dict: The lead record with added enrichment fields:
            - website_snippets: {services, about, blog_headlines}
            - founder_linkedin_posts: [] (placeholder for Phase 2)
            - company_linkedin_posts: [] (placeholder for Phase 2)
            - enrichment_status: "complete" | "partial" | "failed"
            - enrichment_sources: list of sources that yielded data
            - enrichment_timestamp: ISO timestamp
    """
    # Initialize enrichment fields
    lead['founder_linkedin_posts'] = []  # Phase 2
    lead['company_linkedin_posts'] = []  # Phase 2
    lead['website_snippets'] = {
        'services': None,
        'about': None,
        'blog_headlines': []
    }
    lead['enrichment_sources'] = []
    lead['enrichment_timestamp'] = datetime.now(timezone.utc).isoformat()
    
    # Track what we successfully collected
    sources_collected = []
    
    # --- Phase 1: Website Scraping ---
    website_url = lead.get('website') or lead.get('company_website')
    
    if website_url:
        try:
            website_data = scrape_website(website_url)
            
            if website_data.get('success'):
                lead['website_snippets'] = {
                    'services': website_data.get('services'),
                    'about': website_data.get('about'),
                    'blog_headlines': website_data.get('blog_headlines', [])
                }
                
                if website_data.get('sources_found'):
                    sources_collected.append('website')
                    
        except Exception as e:
            print(f"    Warning: Website scraping failed for {website_url}: {e}")
    
    # --- Phase 2: LinkedIn Scraping (Placeholder) ---
    # TODO: Implement in Phase 2
    # founder_linkedin_url = lead.get('founder_linkedin_url')
    # company_linkedin_url = lead.get('company_linkedin_url')
    
    # --- Determine enrichment status ---
    lead['enrichment_sources'] = sources_collected
    
    if len(sources_collected) >= 2:
        # Multiple sources = complete (once LinkedIn is added)
        lead['enrichment_status'] = 'complete'
    elif len(sources_collected) == 1:
        # At least one source
        lead['enrichment_status'] = 'partial'
    else:
        # No sources succeeded
        lead['enrichment_status'] = 'failed'
    
    return lead


def mark_tier2_skipped(lead):
    """
    Mark a Tier 2 lead as skipped for enrichment.
    
    Args:
        lead (dict): The Tier 2 lead record
        
    Returns:
        dict: The lead with enrichment_status = "skipped"
    """
    lead['enrichment_status'] = 'skipped'
    lead['enrichment_sources'] = []
    lead['enrichment_timestamp'] = datetime.now(timezone.utc).isoformat()
    lead['founder_linkedin_posts'] = []
    lead['company_linkedin_posts'] = []
    lead['website_snippets'] = {
        'services': None,
        'about': None,
        'blog_headlines': []
    }
    return lead


# For standalone testing
if __name__ == "__main__":
    import json
    
    # Test with a sample lead
    test_lead = {
        'company_name': 'Test Company',
        'website': 'https://example.com',
        'tier': 'Tier 1',
        'lead_score': 6
    }
    
    print("Testing lead enrichment...")
    enriched = enrich_lead(test_lead)
    print(json.dumps(enriched, indent=2, default=str))
