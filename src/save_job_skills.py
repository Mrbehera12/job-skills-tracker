
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
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:

        with conn.cursor() as cur:
            cur.execute("""
                SELECT job_id, description
                FROM jobs
                WHERE description IS NOT NULL;
            """)

            jobs = cur.fetchall()

            for job_id, description in jobs:
                skills = extract_skills(description)

                for skill in skills:
                    # Add skill if it does not already exist
                    cur.execute("""
                        INSERT INTO skills (skill_name)
                        VALUES (%s)
                        ON CONFLICT (skill_name) DO NOTHING;
                    """, (skill,))

                    # Find the skill ID
                    cur.execute("""
                        SELECT skill_id
                        FROM skills
                        WHERE skill_name = %s;
                    """, (skill,))

                    skill_id = cur.fetchone()[0]

                    # Connect job with skill
                    cur.execute("""
                        INSERT INTO job_skills (job_id, skill_id)
                        VALUES (%s, %s)
                        ON CONFLICT (job_id, skill_id) DO NOTHING;
                    """, (job_id, skill_id))

    print("Job skills saved successfully!")


if __name__ == "__main__":
    main()
