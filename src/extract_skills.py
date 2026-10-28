
import re

SKILL_DICTIONARY = {
    "Python": ["python"],
    "SQL": ["sql"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Hadoop": ["hadoop"],
    "Apache Spark": ["spark", "apache spark"],
    "Apache Airflow": ["airflow", "apache airflow"],
    "Apache Hive": ["hive", "apache hive"],
    "Apache Storm": ["storm", "apache storm"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
}

def extract_skills(text):
    if not text:
        return []

    found_skills = []

    for skill, aliases in SKILL_DICTIONARY.items():
        for alias in aliases:
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"

            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)
                break

    return found_skills


if __name__ == "__main__":
    sample = """
    We need a Data Engineer with AWS, PostgreSQL and Docker.
    """

    skills = extract_skills(sample)

    print("Detected skills:", skills)
