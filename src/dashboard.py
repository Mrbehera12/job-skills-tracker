
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import psycopg
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "job_tracker"
DB_USER = os.getenv("PGUSER") or os.getenv("USER") or "postgres"
DB_HOST = os.getenv("PGHOST", "localhost")
DB_PORT = os.getenv("PGPORT", "5432")

st.set_page_config(
    page_title="Job Market Skills Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Job Market Skills Tracker")
st.caption("Explore detected skills in Data Engineer job postings")

@st.cache_data(ttl=60)
def load_data():
    with psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host=DB_HOST,
        port=DB_PORT
    ) as conn:
        jobs = pd.read_sql(
            "SELECT COUNT(*) AS total_jobs FROM jobs;",
            conn
        ).iloc[0, 0]

        skills = pd.read_sql(
            "SELECT COUNT(*) AS total_skills FROM skills;",
            conn
        ).iloc[0, 0]

        summary = pd.read_sql("""
            SELECT
                s.skill_name AS skill,
                COUNT(DISTINCT js.job_id) AS job_count
            FROM skills s
            JOIN job_skills js
                ON s.skill_id = js.skill_id
            GROUP BY s.skill_name
            ORDER BY job_count DESC, s.skill_name;
        """, conn)

    if jobs:
        summary["percentage"] = (
            summary["job_count"] / jobs * 100
        ).round(1)
    else:
        summary["percentage"] = 0.0

    return jobs, skills, summary


try:
    total_jobs, total_skills, summary = load_data()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Jobs", total_jobs)
    col2.metric("Unique Skills", total_skills)
    col3.metric(
        "Skill Relationships",
        int(summary["job_count"].sum())
    )

    st.subheader("Top Demanded Skills")

    top_skills = summary.head(10)

    fig = px.bar(
        top_skills.sort_values("job_count"),
        x="job_count",
        y="skill",
        orientation="h",
        text="job_count",
        labels={
            "job_count": "Number of Jobs",
            "skill": "Skill"
        },
        title="Skills by Number of Job Postings"
    )

    fig.update_layout(yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Skill Summary")
    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error("Unable to load dashboard data.")
    st.exception(e)
