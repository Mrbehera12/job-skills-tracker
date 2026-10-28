import json
import os
from pathlib import Path
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

load_dotenv()

# 1. Database connection settings
DB_NAME = "job_tracker"
DB_USER = os.getenv("PGUSER", os.getenv("USER", "postgres"))
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")

# 2. Find our latest JSON file
files = sorted(
    Path("data/raw").glob("adzuna_jobs_*.json")
)

if not files:
    raise FileNotFoundError("No saved Adzuna JSON files found")

file_path = files[-1]

print("Reading:", file_path)

with file_path.open(encoding="utf-8") as f:
    data = json.load(f)

jobs = data.get("results", [])
print("Jobs found:", len(jobs))

# 3. Prepare SQL statement
sql = """
INSERT INTO jobs (
    job_id,
    title,
    company,
    location,
    description,
    created_at,
    job_url,
    raw_data,
    collected_at
)
VALUES (
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s
)
ON CONFLICT (job_id) DO NOTHING;
"""

# 4. Insert records
inserted = 0
skipped = 0

collected_at = datetime.now(timezone.utc)

with psycopg.connect(
    dbname=DB_NAME,
    user=DB_USER,
    host=DB_HOST,
    port=DB_PORT,
) as conn:

    with conn.cursor() as cur:

        for job in jobs:

            job_id = job.get("id")

            if job_id is None:
                skipped += 1
                continue

            # Extract nested values
            company_data = job.get("company") or {}
            location_data = job.get("location") or {}

            company = (
                company_data.get("display_name")
                if isinstance(company_data, dict)
                else None
            )

            location = (
                location_data.get("display_name")
                if isinstance(location_data, dict)
                else None
            )

            # Convert source date
            created = job.get("created")
            created_at = None

            if created:
                try:
                    created_at = datetime.fromisoformat(
                        created.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    created_at = None

            cur.execute(
                sql,
                (
                    str(job_id),
                    job.get("title"),
                    company,
                    location,
                    job.get("description"),
                    created_at,
                    job.get("redirect_url"),
                    psycopg.types.json.Jsonb(job),
                    collected_at,
                ),
            )

            if cur.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

print("\nLoading completed!")
print("Inserted:", inserted)
print("Skipped:", skipped)