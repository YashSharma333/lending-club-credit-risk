"""Load the LendingClub CSV into the MySQL `loan_portfolio` table.

Run sql/01_schema.sql first: it creates the typed table this script fills.
"""
import time

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from db import ROOT, get_engine

CSV_PATH = ROOT / "data" / "accepted_2007_to_2018Q4.csv"
TABLE = "loan_portfolio"
CHUNK_SIZE = 50_000

COLUMNS_TO_KEEP = [
    "id", "loan_amnt", "term", "int_rate", "installment", "grade", "sub_grade",
    "emp_length", "home_ownership", "annual_inc", "verification_status",
    "issue_d", "loan_status", "purpose", "addr_state", "dti", "delinq_2yrs",
    "fico_range_low", "fico_range_high", "inq_last_6mths", "revol_bal",
    "revol_util", "total_pymnt", "recoveries", "last_pymnt_d",
]
RENAME = {"id": "loan_id"}


def run_ingestion():
    if not CSV_PATH.exists():
        raise SystemExit(
            f"CSV not found: {CSV_PATH}\n"
            "Download accepted_2007_to_2018Q4.csv and put it in the data/ folder."
        )

    engine = get_engine()

    # Start from an empty table so re-running the script never duplicates rows.
    try:
        with engine.begin() as conn:
            conn.execute(text(f"TRUNCATE TABLE {TABLE}"))
    except ProgrammingError:
        raise SystemExit(f"Table '{TABLE}' not found. Run sql/01_schema.sql first.")

    print("Initiating data pipeline...")
    start_time = time.time()
    total_processed = 0

    for chunk in pd.read_csv(CSV_PATH, usecols=COLUMNS_TO_KEEP,
                             chunksize=CHUNK_SIZE, low_memory=False):
        chunk = chunk.rename(columns=RENAME)
        chunk = chunk.dropna(subset=["loan_status"])  # drops blank / footer rows
        chunk.to_sql(name=TABLE, con=engine, if_exists="append", index=False)

        total_processed += len(chunk)
        print(f"Successfully loaded {total_processed:,} rows into MySQL...")

    elapsed = round(time.time() - start_time, 2)
    print(f"\nPipeline Complete! {total_processed:,} rows ingested.")
    print(f"Execution Time: {elapsed} seconds")


if __name__ == "__main__":
    run_ingestion()
