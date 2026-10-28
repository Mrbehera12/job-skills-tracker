import pandas as pd
import streamlit as st
import plotly.express as px
import psycopg
from streamlit.errors import StreamlitSecretNotFoundError

st.set_page_config(
    page_title="Job Market Skills Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Job Market Skills Tracker")
st.caption("Explore detected skills in Data Engineer job postings")

def get_connection():
    try:
        database_url = st.secrets["DATABASE_URL"]
    except (StreamlitSecretNotFoundError, KeyError):
        st.error(
            "The DATABASE_URL secret is missing. Add it to the app's "
            "Streamlit secrets, then redeploy."
        )
        st.stop()

    return psycopg.connect(
        database_url,
        connect_timeout=10
    )


@st.cache_data(ttl=60)
def load_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM jobs;")
            jobs_result = cur.fetchone()
            if jobs_result is None:
                raise RuntimeError("The jobs count query returned no result.")
            total_jobs = jobs_result[0]

            cur.execute("SELECT COUNT(*) FROM skills;")
            skills_result = cur.fetchone()
            if skills_result is None:
                raise RuntimeError("The skills count query returned no result.")
            total_skills = skills_result[0]

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

    if total_jobs:
        summary["percentage"] = (
            summary["job_count"] / total_jobs * 100
        ).round(1)
    else:
        summary["percentage"] = 0.0

    return total_jobs, total_skills, summary


try:
    total_jobs, total_skills, summary = load_data()

    total_relationships = int(summary["job_count"].sum())

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Jobs", total_jobs)
    col2.metric("Unique Skills", total_skills)
    col3.metric("Skill Relationships", total_relationships)

    st.subheader("Top Demanded Skills")

    top_skills = summary.head(10)

    if not top_skills.empty:
        chart_data = top_skills.sort_values("job_count")

        fig = px.bar(
            chart_data,
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

        st.plotly_chart(
            fig,
            width="stretch"
        )
    else:
        st.info("No detected skills are available yet.")

    st.subheader("Skill Summary")

    st.dataframe(
        summary,
        width="stretch",
        hide_index=True
    )


except psycopg.errors.UndefinedTable:
    st.error(
        "The database is missing a required table. Run "
        "`src/schema.sql` against the deployment database, then refresh."
    )
except psycopg.OperationalError as error:
    st.error(
        "Unable to connect to the database. Verify DATABASE_URL, the "
        "database's availability, and its network access settings."
    )
    st.exception(error)
except psycopg.Error as error:
    st.error("The database rejected a dashboard query.")
    st.exception(error)
