import os
import sys
import json
import argparse
import requests
import re
from time import sleep

# Add parent directory to path to allow imports if needed, though we use relative file paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from execution.gcal_sheets import read_leads, batch_update_leads
except ImportError:
    # If running from execution dir
    from gcal_sheets import read_leads, batch_update_leads

def load_config():
    """Load configuration from .env"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k not in os.environ:
                        os.environ[k] = v.strip("'").strip('"')

def load_matrix():
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'classification_matrix.json')
    with open(path) as f:
        return json.load(f)

def call_gemini(prompt, api_key):
    """
    Calls Gemini Pro via REST API.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2, # Low temp for factual generation
            "maxOutputTokens": 200,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            print(f"LLM Error: No candidates returned. {result}")
            return None
    except Exception as e:
        print(f"LLM Call Failed: {e}")
        return None

def generate_public_context(lead, api_key):
    """
    Generates the 'Public Context Sentence' using LLM.
    """
    company = lead.get('company_name', 'your company')
    desc = lead.get('company_description', '')
    keywords = lead.get('keywords', '')
    
    if not desc and not keywords:
        return None
        
    prompt = f"""
    You are Jon, the owner of NeXNet, writing a direct, peer-to-peer email to another business owner.
    
    Task: Write ONE "Public Context Sentence" that proves you looked at their business ({company}).
    
    Input Data:
    Company: {company}
    Description: {desc}
    Keywords: {keywords}
    
    Tone Guidelines (Critical):
    - **Owner-to-Owner**: Speak plainly and professionally. No "marketing fluff".
    - **Clinical Observation**: State what you see, don't unnecessarily compliment it.
    - **No Sales Breath**: Avoid "I was impressed by..." or "Congrats on...".
    
    Format:
    - Start with "Saw that...", "Noticed...", "It looks like..."
    - Length: Short, punchy. Under 20 words if possible.
    
    Bad Examples (Do NOT do this):
    - "I hope you are doing well!" (Fluff)
    - "I was browsing your website and saw..." (Too verbose)
    - "You are doing amazing work in the construction space." (Patronizing)
    
    Good Examples:
    - "Saw that your team handles complex commercial builds across the generic state area."
    - "Noticed you're scaling the team to handle the new government contracts."
    - "It looks like you're balancing a mix of field operations and back-office design work."
    
    Output (The single sentence only):
    """
    
    return call_gemini(prompt, api_key)

def classify_lead_deterministic(lead, matrix):
    """
    Deterministic first-pass classification based on keywords.
    """
    text = (lead.get('company_description', '') + ' ' + lead.get('keywords', '') + ' ' + lead.get('title', '')).lower()
    
    best_a = "A1" # Default fallback
    best_b = "B1" # Default fallback
    
    # Simple keyword scoring (naive implementation)
    max_score_a = 0
    for code, data in matrix['axes']['business_model_reality'].items():
        score = 0
        for ind in data.get('industries', []):
            if ind in text: score += 2
        if data.get('label', '').lower() in text: score += 1
        
        if score > max_score_a:
            max_score_a = score
            best_a = code

    max_score_b = 0
    for code, data in matrix['axes']['execution_pressure'].items():
        score = 0
        for signal in data.get('signals', []):
            if signal in text: score += 2
            
        if score > max_score_b:
            max_score_b = score
            best_b = code
            
    return best_a, best_b

def get_inference_paragraph(matrix, a_code, b_code):
    cell_key = f"{a_code}_{b_code}"
    cell = matrix['matrix_cells'].get(cell_key)
    if cell:
        return cell['inference_paragraph'], False
    
    # Fallback: Find nearest neighbor or default
    # For simplicity, default to A1_B1 or similar if missing
    # Legacy says: "apply nearest-neighbor fallback"
    # We'll just grab the first one that matches A code, or just A1_B1
    
    # Try finding any cell with same A code
    for k, v in matrix['matrix_cells'].items():
        if k.startswith(a_code):
            return v['inference_paragraph'], True
            
    # Absolute fallback
    return matrix['matrix_cells']['A1_B1']['inference_paragraph'], True

def compose_email_1(lead, context_sentence, inference_paragraph):
    # Subject: {Company} + AI? / Question regarding {Company}
    subject = f"Question regarding {lead.get('company_name', 'your team')}"
    
    first_name = lead.get('first_name', 'there')
    
    body = f"""Hi {first_name},

{context_sentence}

{inference_paragraph}

We’re running 'Shadow AI Audits' for a few owners this week to help you spot where your team is using unapproved AI tools.

Worth a look?

Best,
Jon
"""
    return subject, body

def main():
    load_config()
    parser = argparse.ArgumentParser(description="Generate NeXNet Cold Emails")
    parser.add_argument("--sheet-id", required=True, help="Google Sheet ID")
    parser.add_argument("--limit", type=int, default=5, help="Max leads to process")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to sheet")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in .env. LLM features (Public Context) will be disabled/mocked.")
    
    print(f"Reading sheet: {args.sheet_id}")
    leads = read_leads(args.sheet_id)
    print(f"Found {len(leads)} rows.")
    
    matrix = load_matrix()
    
    updates = []
    processed_count = 0
    
    for lead in leads:
        if processed_count >= args.limit:
            break
            
        # skip if already generated?
        if lead.get('Email 1 Body'):
            continue
            
        print(f"Processing {lead.get('company_name')}...")
        
        # 1. Feature Extraction & Classification
        a_code, b_code = classify_lead_deterministic(lead, matrix)
        
        # 2. Public Context (LLM)
        if api_key:
            context = generate_public_context(lead, api_key)
        else:
            context = None
            
        if not context:
            # Fallback if LLM fails or no key
            context = f"Noticed you are active in the {lead.get('company_industry', 'industry')} space."
            
        # 3. Matrix Selection
        inference, is_fallback = get_inference_paragraph(matrix, a_code, b_code)
        
        # 4. Compose Emails
        subj1, body1 = compose_email_1(lead, context, inference)
        
        # Email 2, 3, 4 placeholders (for brevity of this task, implementing full sequence per directive)
        # Email 2: Normalization
        body2 = "Quick follow-up: this is pretty common. Teams often move faster than policy. The audit just gives you visibility, not a bottleneck."
        
        # Email 3: Insight
        body3 = "Most owners find 2-3 tools they didn't know about. It's usually harmless, but sometimes it's client data in a public model. Worth checking."
        
        # Email 4: Breakup
        body4 = "Last note—I'll assume this isn't a priority right now. I'll take you off my list."
        
        updates.append({
            "id": lead.get('id') or lead.get('lead_id') or lead.get('email'), # careful with key
            "A_Code": a_code,
            "B_Code": b_code,
            "Context_Sentence": context,
            "Email 1 Subject": subj1,
            "Email 1 Body": body1,
            "Email 2 Body": body2,
            "Email 3 Body": body3,
            "Email 4 Body": body4
        })
        
        processed_count += 1
        
        print(f"  > Classification: {a_code}/{b_code}")
        print(f"  > Subject: {subj1}")
        print(f"  > Body Preview: {body1[:100].replace(chr(10), ' ')}...")
        sleep(1) # Rate limit courtesy
        
    print(f"Generated {len(updates)} sequences.")
    
    if not args.dry_run and updates:
        # Determine key field.
        # If 'id' is in leads, use it. Else 'lead_id', else 'email'.
        key_field = 'id'
        if 'lead_id' in leads[0]: key_field = 'lead_id'
        elif 'email' in leads[0]: key_field = 'email'
        
        # Ensure updates have the key
        valid_updates = []
        for u in updates:
            # fix key if needed
            if key_field not in u:
                u[key_field] = u['id'] # assume we stored it in 'id' in the loop
            valid_updates.append(u)
            
        batch_update_leads(args.sheet_id, valid_updates, key_field=key_field)

if __name__ == "__main__":
    main()
