
import os
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

# 1. Load credentials
load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

if not app_id or not app_key:
    raise ValueError("Missing Adzuna credentials")

# 2. API endpoint
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

# 3. Search parameters
params = {
    "app_id": app_id,
    "app_key": app_key,
    "what": "data engineer",
    "results_per_page": 50,
    "content-type": "application/json",
}

# 4. Request job postings
response = requests.get(
    url,
    params=params,
    timeout=30,
)

# Stop if request fails
response.raise_for_status()

# 5. Check that response is valid JSON
data = response.json()

jobs = data.get("results", [])

print("Total matching jobs reported:", data.get("count"))
print("Jobs returned in this response:", len(jobs))

# 6. Prepare raw data folder
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

# 7. Create a timestamped filename
timestamp = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%SZ"
)

output_file = output_dir / f"adzuna_jobs_{timestamp}.json"

# 8. Save the original response body
output_file.write_text(
    response.text,
    encoding="utf-8",
)

print("Raw API response saved!")
print("File:", output_file)
