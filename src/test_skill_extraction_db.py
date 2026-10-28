
import os
import psycopg
from dotenv import load_dotenv

from extract_skills import extract_skills

load_dotenv()

DB_NAME = "job_tracker"
DB_USER = os.getenv("PGUSER") or os.getenv("USER") or "postgres"
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")

def main():
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT,
    )

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT job_id, title, description
                FROM jobs
                WHERE description IS NOT NULL
                ORDER BY job_id
                LIMIT 1;
            """)

            job = cur.fetchone()

            if job is None:
                print("No job with a description found.")
                return

            job_id, title, description = job

            skills = extract_skills(description)

            print("Job ID:", job_id)
            print("Job title:", title)
            print("Detected skills:", skills)

    finally:
        conn.close()

if __name__ == "__main__":
    main()
