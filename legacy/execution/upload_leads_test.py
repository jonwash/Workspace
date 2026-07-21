import json
import os
import sys

# Add parent to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gcal_sheets import upload_leads

LEAD_FILE = ".tmp/qualified_leads.json"

if not os.path.exists(LEAD_FILE):
    print(f"Error: {LEAD_FILE} not found.")
    sys.exit(1)

with open(LEAD_FILE) as f:
    leads = json.load(f)

# Take top 5 for speed
test_leads = leads[:5]
print(f"Uploading {len(test_leads)} leads for testing...")

# We pass a None sheet_id to force creation of a new one
url = upload_leads(test_leads, sheet_id=None, query="Cold Email Test", industry="Test", location="Lab")

print(f"TEST SHEET URL: {url}")
# Extract ID from URL for next step
# URL format: https://docs.google.com/spreadsheets/d/SHEET_ID/edit
sheet_id = url.split("/d/")[1].split("/")[0]
print(f"SHEET ID: {sheet_id}")

# Save ID to a temp file so we can grab it easily
with open(".tmp/test_sheet_id.txt", "w") as f:
    f.write(sheet_id)
