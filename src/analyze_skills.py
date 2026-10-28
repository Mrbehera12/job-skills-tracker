import csv
from pathlib import Path
import os
from collections import Counter

import psycopg
from dotenv import load_dotenv

from extract_skills import extract_skills

load_dotenv()

DB_NAME = "job_tracker"
DB_USER = os.getenv("PGUSER") or os.getenv("USER") or "postgres"
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")


def main():
    skill_counts = Counter()
    processed_jobs = 0

    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT,
    ) as conn:

        with conn.cursor() as cur:
            cur.execute("""
                SELECT job_id, title, description
                FROM jobs
                WHERE description IS NOT NULL;
            """)

            for job_id, title, description in cur.fetchall():
                skills = extract_skills(description)

                # Count each skill at most once per job
                skill_counts.update(set(skills))
                processed_jobs += 1

    print("Jobs processed:", processed_jobs)
    print("\nTop detected skills:")

    for skill, count in skill_counts.most_common(15):
        percentage = count / processed_jobs * 100 if processed_jobs else 0
        print(f"{skill}: {count} jobs ({percentage:.1f}%)")

    output_path = Path("data/processed/skill_summary.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "job_count", "percentage"])

        for skill, count in skill_counts.most_common():
            percentage = count / processed_jobs * 100 if processed_jobs else 0
            writer.writerow([skill, count, round(percentage, 1)])

    print(f"\nSaved analysis to: {output_path}")


if __name__ == "__main__":
    main()
