"""Export the 10 analysis queries to reports/Credit_Risk_Data.xlsx.

Writes a separate file so the hand-built dashboard workbook
(reports/Credit_Risk_Master.xlsx) is never overwritten.
"""
import pandas as pd
from sqlalchemy import text

from db import ROOT, get_engine, load_queries

OUTPUT = ROOT / "reports" / "Credit_Risk_Data.xlsx"
SHEET_NAMES = [
    "Top_KPIs", "ROI_Data", "LGD_Data", "FICO_DTI_Data", "Utilization_Data",
    "Term_Data", "Emp_Length_Data", "Purpose_Data", "Loan_Amount_Data", "State_Data",
]


def main():
    queries = load_queries()
    print(f"Found {len(queries)} queries.")
    if len(queries) != len(SHEET_NAMES):
        raise SystemExit(
            "Expected 10 queries. Check sql/02_risk_analysis.sql: every query must "
            "end with a semicolon, and comments must not contain one."
        )

    engine = get_engine()
    OUTPUT.parent.mkdir(exist_ok=True)

    print("Exporting 10-query dashboard data to Excel...")
    with pd.ExcelWriter(OUTPUT) as writer:
        for query, sheet in zip(queries, SHEET_NAMES):
            # text() lets the SQL use a plain % (no %% escaping needed)
            pd.read_sql(text(query), engine).to_excel(writer, sheet_name=sheet, index=False)

    print(f"Export Complete! See {OUTPUT}")


if __name__ == "__main__":
    main()
