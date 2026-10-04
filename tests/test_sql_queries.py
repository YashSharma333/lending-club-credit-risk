"""Smoke tests for sql/02_risk_analysis.sql.

Runs every query against a small synthetic SQLite table, so no MySQL server
or LendingClub data is needed (this is what GitHub Actions runs).
"""
import random

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from db import load_queries

# Column names the dashboard and Excel export rely on, in query order.
EXPECTED_COLUMNS = [
    ["total_borrowers", "total_loan_amount", "amount_at_risk", "overall_default_rate"],
    ["grade", "total_closed_loans", "total_cap_dep", "net_return", "roi_percentage"],
    ["grade", "total_defaults", "avg_loan_amount", "avg_lgd_percentage", "recovery_rate_percentage"],
    ["fico_bracket", "dti_bracket", "total_loans", "default_rate"],
    ["utilization_bracket", "total_loans", "total_defaults", "default_rate"],
    ["term", "total_loans", "total_defaults", "default_rate"],
    ["employment_duration", "total_loans", "total_defaults", "default_rate"],
    ["purpose", "total_loans", "total_defaults", "default_rate"],
    ["loan_amount_bin", "amount_at_risk", "default_rate"],
    ["state", "amount_at_risk", "default_rate"],
]


@pytest.fixture(scope="module")
def engine():
    random.seed(1)
    rows = []
    for i in range(3000):
        amt = random.choice([5000, 12000, 20000, 30000, 35000])
        rows.append(dict(
            loan_id=i, loan_amnt=amt,
            term=random.choice([" 36 months", " 60 months"]),
            grade=random.choice("ABCDEFG"),
            emp_length=random.choice(["< 1 year", "3 years", "7 years", "10+ years", None]),
            loan_status=random.choice(["Fully Paid", "Charged Off", "Current", "Late (31-120 days)"]),
            purpose=random.choice(["car", "credit_card", "debt_consolidation", "other"]),
            addr_state=random.choice(["CA", "NY", "TX"]),
            dti=random.uniform(0, 40), fico_range_low=random.choice([660, 700, 750]),
            revol_util=random.uniform(0, 100),
            total_pymnt=amt * random.uniform(0.3, 1.2), recoveries=random.uniform(0, 500),
        ))
    eng = create_engine("sqlite://")
    pd.DataFrame(rows).to_sql("loan_portfolio", eng, index=False)
    return eng


def test_file_has_exactly_10_queries():
    # A ';' inside a comment would split a query and break the dashboard.
    assert len(load_queries()) == 10


@pytest.mark.parametrize("index", range(10))
def test_query_runs_and_has_expected_columns(engine, index):
    df = pd.read_sql(text(load_queries()[index]), engine)
    assert list(df.columns) == EXPECTED_COLUMNS[index]
    assert len(df) > 0
