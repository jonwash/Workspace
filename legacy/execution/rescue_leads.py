import os
import argparse
from apify_client import ApifyClient
from gcal_sheets import upload_leads

def load_config():
    if os.path.exists('.env'):
        with open('.env') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    if k not in os.environ:
                        os.environ[k] = v.strip("'").strip('"')

def main():
    load_config()
    run_id = "TofOGxXJBRfvO6jN5"
    share_email = os.environ.get("SHARE_EMAIL", "jon-wash@example.com")
    
    print(f"Rescuing leads from run {run_id}...")
    token = os.environ.get("APIFY_TOKEN")
    client = ApifyClient(token)
    
    # Get run info
    run = client.run(run_id).get()
    dataset_id = run['defaultDatasetId']
    print(f"Dataset ID: {dataset_id}")
    
    # Fetch items
    items = client.dataset(dataset_id).list_items().items
    print(f"Fetched {len(items)} items.")
    
    if items:
        # Check criteria (simplified)
        qualified = [i for i in items if i.get('email') and 'gmail' not in i.get('email', '')]
        print(f"Qualified leads: {len(qualified)}")
        
        # Upload
        try:
            url = upload_leads(qualified, share_email=share_email, query="Accounting (Rescued)")
            print(f"Leads uploaded to: {url}")
        except Exception as e:
            print(f"Error uploading to Sheets: {e}")
            import json
            filename = os.path.join(".tmp", "rescued_leads.json")
            with open(filename, "w") as f:
                json.dump(qualified, f, indent=2)
            print(f"Fallback: Leads saved to {filename}")
    else:
        print("No items found.")

if __name__ == "__main__":
    main()
