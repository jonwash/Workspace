import re

def score_lead(lead):
    """
    Evaluates a lead based on NeXNet Cold Email Scoring Rules.
    
    Inputs: lead (dict) containing 'job_title', 'keywords', 'company_description', 'company_size', etc.
    Returns: enriched lead (dict) with 'score', 'score_breakdown', 'tier', 'outreach_angle'.
    """
    score = 0
    breakdown = []
    
    # Normalize inputs
    title = (lead.get('job_title') or '').lower()
    desc = (lead.get('company_description') or '').lower()
    keywords = (lead.get('keywords') or '').lower()
    headline = (lead.get('headline') or '').lower()
    # senior_level = (lead.get('seniority_level') or '').lower() # Not always reliable, stick to title
    
    # Parse size
    size_str = lead.get('company_size') or 0
    try:
        size = int(size_str)
    except (ValueError, TypeError):
        size = 0

    # --- 1. Founder Role (+2) ---
    founder_titles = ["ceo", "partner", "principal", "owner", "founder", "president", "managing partner"]
    if any(t in title for t in founder_titles):
        score += 2
        breakdown.append("Founder Role (+2)")
        
    # --- 2. No Internal IT (+2) ---
    # We look for IT roles in the *description* or *keywords* as a proxy for "team structure" mentioned in text
    # BUT, typically we check the specific contact's role. 
    # The directive implies: "No internal IT staff listed". 
    # Since we are scraping a single *decision maker*, we can't see the whole team.
    # PROXY: If they mention "IT Department" or "CTO" in their description, that's a negative signal.
    # Wait, the rule is "No internal IT role". 
    # If we find "IT Manager", "System Admin" in keywords/desc, we assume they HAVE IT -> 0 points.
    # If we DO NOT find these, we assume NO IT -> +2 points.
    it_roles = ["it manager", "cto", "cio", "system admin", "network admin", "director of it", "director of technology"]
    has_it_signal = any(r in desc for r in it_roles) or any(r in keywords for r in it_roles)
    
    if not has_it_signal:
        score += 2
        breakdown.append("No Internal IT Signal (+2)")

    # --- 3. Document-Heavy (+1) ---
    doc_terms = ["files", "records", "audit", "tax", "legal", "compliance", "case files", "reports", "plans", "paperwork"]
    if any(t in desc for t in doc_terms) or any(t in keywords for t in doc_terms):
        score += 1
        breakdown.append("Document-Heavy (+1)")

    # --- 4. Compliance/Confidentiality (+1) ---
    comp_terms = ["confidential", "compliance", "regulation", "regulatory", "hipaa", "finra", "sec", "gdpr", "private"]
    if any(t in desc for t in comp_terms) or any(t in keywords for t in comp_terms):
        score += 1
        breakdown.append("Compliance Focused (+1)")

    # --- 5. Size 15+ (+1) ---
    if size >= 15:
        score += 1
        breakdown.append("Size 15+ (+1)")

    # --- 6. Admin Handles IT (+1) ---
    # Difficult to detect without team scrape. 
    # Heuristic: If "Office Manager" is mentioned in description/keywords near "technology" or "systems".
    # For now, we will be conservative and only award if we see "office manager" AND "systems" or "setup".
    if "office manager" in desc and ("system" in desc or "setup" in desc or "technology" in desc):
        score += 1
        breakdown.append("Admin/Ops handles IT (+1)")

    # --- TIER ASSIGNMENT ---
    # Threshold: 6+
    tier = "Tier 1" if score >= 6 else "Tier 2"
    angle = "Shadow AI & Access Audit" if tier == "Tier 1" else "Generic/Nurture"

    # Enrich Lead
    lead['lead_score'] = score
    lead['score_breakdown'] = "; ".join(breakdown)
    lead['tier'] = tier
    lead['outreach_angle'] = angle
    
    return lead
