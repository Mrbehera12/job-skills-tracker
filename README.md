# job-skills-tracker
A data engineering and NLP project to analyze job market skills.

## Run the dashboard

Install the dependencies and start Streamlit from the repository root:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The dashboard uses PostgreSQL. Set `DATABASE_URL` in Streamlit secrets before
starting the app. For local development, create
`.streamlit/secrets.toml` (this file must not be committed):

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
```

For Streamlit Community Cloud, select `streamlit_app.py` as the app file and
add the same `DATABASE_URL` value in the app's **Settings → Secrets**. The
database must be reachable from the deployment, and its user must be allowed
to create tables. The dashboard creates its tables in the `public` schema on
first load. If the database user cannot create tables, run `src/schema.sql`
from the database provider's SQL editor as the database owner. Creating the
tables does not load job data or skill relationships; the dashboard can run
with empty tables, but it will have no job or skill data to display.
