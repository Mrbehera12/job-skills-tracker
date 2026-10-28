import json
from pathlib import Path

# Find JSON files
files = sorted(Path("data/raw").glob("adzuna_jobs_*.json"))

if not files:
    raise FileNotFoundError("No Adzuna JSON files found")

# Select the most recently named collection file
file_path = files[-1]

print("Reading:", file_path)

# Load JSON
with file_path.open(encoding="utf-8") as f:
    data = json.load(f)

jobs = data.get("results", [])

print("Jobs in file:", len(jobs))

if not jobs:
    print("No job postings found")
    raise SystemExit

job = jobs[0]

# Show top-level fields
print("\nFields in first job:")
for key, value in job.items():
    print(f"{key}: {type(value).__name__}")

# Show nested company fields
company = job.get("company", {})
if isinstance(company, dict):
    print("\nCompany fields:", list(company.keys()))

# Show nested location fields
location = job.get("location", {})
if isinstance(location, dict):
    print("Location fields:", list(location.keys()))

# Show a few safe example values
print("\nExample:")
for key in ["id", "title", "created"]:
    print(f"{key}:", job.get(key))

print("Company:", company.get("display_name")
      if isinstance(company, dict) else None)

print("Location:", location.get("display_name")
      if isinstance(location, dict) else None)
