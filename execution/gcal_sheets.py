import os
import json
import argparse
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

def get_or_create_sheet(sheet_id=None, share_email=None, query="Lead Gen", industry=None, location=None, credentials_file='credentials.json'):
    """
    Opens an existing sheet or creates a new one.
    Returns: sheet object, sheet_url
    """
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    
    # Domain-Wide Delegation: Impersonate a user to avoid Service Account quota limits
    delegated_user = os.environ.get('DELEGATED_USER')
    if delegated_user:
        print(f"Server Account delegating to: {delegated_user}")
        creds = creds.with_subject(delegated_user)
        
    gc = gspread.authorize(creds)
    
    if sheet_id:
        if sheet_id == "MOCK_SHEET_ID_FOR_DRY_RUN":
            print("MOCK MODE: Returning mock sheet object.")
            # Create a mock object that mimics a spreadsheet -> worksheet
            class MockSheet:
                class MockWorksheet:
                    def get_all_records(self):
                        # Return dummy data for testing
                        return [
                            {
                                "lead_id": "mock_1", "company_name": "Mock Construction Co", 
                                "company_description": "We specialize in residential remodeling and custom homes.",
                                "keywords": "construction, remodeling", "first_name": "Bob", "title": "Owner", "company_industry": "Construction"
                            },
                            {
                                "lead_id": "mock_2", "company_name": "Mock MSP", 
                                "company_description": "Managed IT services for law firms.",
                                "keywords": "msp, it support", "first_name": "Alice", "title": "CEO", "company_industry": "Information Technology"
                            }
                        ]
                    def update_cells(self, cells): pass
                    def add_cols(self, n): pass
                    def row_values(self, n): return []
                
                sheet1 = MockWorksheet()
                url = "http://mock-url"
            
            return MockSheet(), "http://mock-url"

        print(f"Opening existing sheet: {sheet_id}")
        sh = gc.open_by_key(sheet_id)
        return sh, sh.url

    # Construct Standard Name if possible
    if industry and location:
        sheet_name = f"NeXNet Leads - {industry} - {location}"
    else:
        # Fallback for manual/test runs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet_name = f"NeXNet Leads - {query} - {timestamp}"

    # Try to find existing sheet by name
    try:
        sh = gc.open(sheet_name)
        print(f"Found existing sheet: '{sheet_name}'")
    except gspread.SpreadsheetNotFound:
        print(f"Creating new sheet: '{sheet_name}'")
        sh = gc.create(sheet_name)
        
        if share_email:
            print(f"Sharing sheet with {share_email}...")
            sh.share(share_email, perm_type='user', role='writer')
        else:
            print("Warning: No share email provided. The sheet is created but only accessible by the service account.")
            
    return sh, sh.url

def upload_leads(leads, sheet_id=None, share_email=None, query="Lead Gen", industry=None, location=None, credentials_file='credentials.json'):
    """
    Uploads list of leads (dicts) to a Google Sheet.
    """
    sh, url = get_or_create_sheet(sheet_id, share_email, query, industry, location, credentials_file)
    worksheet = sh.sheet1
    
    print(f"Uploading {len(leads)} leads...")
    if not leads:
        print("No leads to upload.")
        return url

    headers = list(leads[0].keys())
    rows = [[str(lead.get(k, '')) for k in headers] for lead in leads]
    
    # Send headers if new sheet or empty
    # Check A1 specifically, as new sheets have 1000 empty rows
    if not worksheet.acell('A1').value:
        worksheet.append_row(headers)
        
    worksheet.append_rows(rows)
    print("Upload complete.")
    return url

def read_leads(sheet_id):
    """
    Reads all records from the first worksheet of the given sheet_id.
    Returns: List of dicts
    """
    sh, _ = get_or_create_sheet(sheet_id=sheet_id)
    worksheet = sh.sheet1
    return worksheet.get_all_records()

def update_lead_row(sheet_id, lead_id, update_dict, id_column="lead_id"):
    """
    Updates a specific row where id_column matches lead_id.
    Note: This is slow for bulk updates. For batch, usage of cell updates is better.
    """
    sh, _ = get_or_create_sheet(sheet_id=sheet_id)
    worksheet = sh.sheet1
    
    # improved batch update logic could go here, but for now linear scan/find is simple
    # assuming lead_id is unique
    pass 
    # Actually, let's implement a bulk update for the generator
    
def batch_update_leads(sheet_id, updates_list, key_field="id"):
    """
    Updates multiple rows.
    updates_list: list of dicts, each must contain the key_field.
    """
    sh, _ = get_or_create_sheet(sheet_id=sheet_id)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    
    # Map key to row index (1-based, +1 for header)
    key_map = {str(row.get(key_field)): i + 2 for i, row in enumerate(data) if row.get(key_field)}
    
    cells_to_update = []
    headers = data[0].keys() if data else []
    header_map = {h: i + 1 for i, h in enumerate(headers)} # col name -> col index
    
    # If new columns are introduced in updates, we might need to add them?
    # For now, assume columns exist or we add them. 
    # Simplification: Just update existing columns or fail?
    # The directive says "Outputs are written back to the same Google Sheet row".
    # We should probably ensure columns like "Email 1 Subject" exist.
    
    # Let's verify headers first
    all_keys = set()
    for u in updates_list:
        all_keys.update(u.keys())
    
    existing_headers = set(header_map.keys())
    new_headers = [k for k in all_keys if k not in existing_headers and k != key_field]
    
    if new_headers:
        print(f"Adding new columns: {new_headers}")
        # Add headers to row 1
        worksheet.add_cols(len(new_headers))
        # This is tricky with gspread to find the next free column efficiently without reading expected len.
        # simpler: just get current values of row 1
        current_headers = worksheet.row_values(1)
        next_col_idx = len(current_headers) + 1
        
        # update header map
        header_updates = []
        for i, h in enumerate(new_headers):
            # Row 1, Col next_col_idx + i
            # Cell(row, col, value)
            cells_to_update.append(gspread.Cell(1, next_col_idx + i, h))
            header_map[h] = next_col_idx + i
            
    for update in updates_list:
        key = str(update.get(key_field))
        if key in key_map:
            row_idx = key_map[key]
            for field, value in update.items():
                if field == key_field: continue
                if field in header_map:
                    col_idx = header_map[field]
                    cells_to_update.append(gspread.Cell(row_idx, col_idx, str(value)))
    
    if cells_to_update:
        print(f"Updating {len(cells_to_update)} cells...")
        worksheet.update_cells(cells_to_update)
        print("Update complete.")
    else:
        print("No updates made.")

if __name__ == "__main__":
    def load_config():
        """Load configuration from .env or environment variables."""
        if os.path.exists('.env'):
            with open('.env') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            k, v = line.split('=', 1)
                            if k not in os.environ:
                                v = v.strip("'").strip('"')
                                os.environ[k] = v

    load_config()
    parser = argparse.ArgumentParser(description="Upload JSON leads to Google Sheets")
    parser.add_argument("file", help="Path to JSON file containing leads")
    parser.add_argument("--share", help="Email to share the sheet with", default=os.environ.get("SHARE_EMAIL"))
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
    else:
        with open(args.file, 'r') as f:
            leads = json.load(f)
            
        print(f"Loaded {len(leads)} leads from {args.file}")
        
        try:
            url = upload_leads(leads, share_email=args.share, query=f"Upload of {os.path.basename(args.file)}")
            print(f"Success! View your sheet here: {url}")
        except Exception as e:
            print(f"Upload failed: {e}")
