from apify_client import ApifyClient

def run_scraper(run_input, apify_token):
    """
    Executes an Apify actor with the provided dictionary input.
    """
    client = ApifyClient(apify_token)
    print(f"Running scraper with inputs: {run_input}...")
    
    # Using code_crafter/leads-finder with structured inputs
    run = client.actor("code_crafter/leads-finder").call(run_input=run_input)
    
    dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
    return dataset_items
