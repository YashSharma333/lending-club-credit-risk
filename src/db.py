"""Shared helpers used by the ingest, export and dashboard scripts."""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_SQL = ROOT / "sql" / "02_risk_analysis.sql"

load_dotenv(ROOT / ".env")


def get_engine():
    """Build a MySQL engine from the DB_* values in .env."""
    required = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            f"Missing {', '.join(missing)} in .env (copy .env.example to .env)."
        )
    url = URL.create(
        "mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),  # special characters are escaped safely
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(url)


def load_queries(path=ANALYSIS_SQL):
    """Split the analysis SQL file into its individual SELECT queries."""
    script = Path(path).read_text()
    queries = []
    for chunk in script.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        code = re.sub(r"--.*", "", chunk)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL).strip()
        if code.upper().startswith(("SELECT", "WITH")):
            queries.append(chunk)
    return queries
