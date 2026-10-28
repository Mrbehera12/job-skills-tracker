
import os
import requests
from dotenv import load_dotenv

# Read credentials from .env
load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

if not app_id or not app_key:
    raise ValueError("Missing Adzuna API credentials in .env")

# API endpoint
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# Search settings
params = {
    "app_id": app_id,
    "app_key": app_key,
    "what": "data engineer",
    "results_per_page": 50,
    "content-type": "application/json",
}

# Send request
response = requests.get(
    url,
    params=params,
    timeout=30
)

# Stop if the request failed
response.raise_for_status()

# Convert JSON response into Python data
data = response.json()

# Read job results
jobs = data.get("results", [])

print("Matching jobs:", data.get("count"))

if jobs:
    job = jobs[0]

    print("\nFirst job")
    print("Title:", job.get("title"))
    print("Company:", job.get("company", {}).get("display_name"))
    print("Location:", job.get("location", {}).get("display_name"))
    print("Job ID:", job.get("id"))
    print("Posted:", job.get("created"))
else:
    print("No jobs returned. Try another search.")
