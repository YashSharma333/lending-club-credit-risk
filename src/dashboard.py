import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import text

from db import get_engine, load_queries

# 1. Page Configuration (Wide layout for BI Dashboard)
st.set_page_config(page_title="Credit Risk Dashboard", layout="wide")
st.title("Portfolio Risk & Yield Analysis")
st.markdown("### 2007-2018 Originations (closed loans only)")


# 2. Database Connection (Cached)
@st.cache_resource
def init_connection():
    return get_engine()


engine = init_connection()


# 3. Data Loading (Cached to prevent re-running SQL on every click)
@st.cache_data
def load_data():
    # text() lets the SQL use a plain % (no %% escaping needed)
    return [pd.read_sql(text(query), engine) for query in load_queries()]


try:
    data = load_data()
    kpi_df, roi_df, lgd_df, fico_dti_df, utilization_df, term_df, emp_length_df, purpose_df, loan_amount_df, state_df = data
except Exception as e:
    st.error(f"Error loading data. Check your SQL file. Details: {e}")
    st.stop()


def donut(df, category, value, height=280):
    """Doughnut chart: use ONLY for parts of a whole (slices add up to 100%)."""
    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta(f"{value}:Q"),
            color=alt.Color(f"{category}:N", legend=alt.Legend(title=None)),
            tooltip=[category, alt.Tooltip(f"{value}:Q", format=",")],
        )
        .properties(height=height)
    )
    st.altair_chart(chart, use_container_width=True)


# ==========================================
# DASHBOARD LAYOUT & VISUALS
# ==========================================

# ROW 1: Top KPI Ribbon
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Closed Loans", f"{kpi_df['total_borrowers'].iloc[0]:,}")
with col2:
    st.metric("Total Loan Volume", f"${kpi_df['total_loan_amount'].iloc[0]:,.0f}")
with col3:
    st.metric("Charged-Off Principal", f"${kpi_df['amount_at_risk'].iloc[0]:,.0f}")
with col4:
    st.metric("Portfolio Default Rate", f"{kpi_df['overall_default_rate'].iloc[0]}%")

st.markdown("---")

# ROW 2: Where do defaults come from? (doughnuts = share of all defaults)
col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.subheader("Share of Defaults by Term")
    donut(term_df, 'term', 'total_defaults')

with col_mid:
    st.subheader("Share of Defaults by Employment")
    donut(emp_length_df, 'employment_duration', 'total_defaults')

with col_right:
    st.subheader("Default Rate by Loan Purpose")
    purpose_sorted = purpose_df.sort_values('default_rate', ascending=False)
    st.dataframe(purpose_sorted[['purpose', 'total_loans', 'default_rate']],
                 hide_index=True, use_container_width=True)

st.markdown("---")

# ROW 3: How risky is each group? (bars = rates, so groups can be compared)
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Default Rate by Credit Utilization (%)")
    st.bar_chart(data=utilization_df.set_index('utilization_bracket')['default_rate'])

with col_b:
    st.subheader("Default Rate by Loan Amount (%)")
    st.bar_chart(data=loan_amount_df.set_index('loan_amount_bin')['default_rate'])

st.markdown("---")

# ROW 4: Dollars at risk
col_bottom_left, col_bottom_right = st.columns(2)

with col_bottom_left:
    st.subheader("Charged-Off Principal by Loan Bracket ($)")
    st.bar_chart(data=loan_amount_df.set_index('loan_amount_bin')['amount_at_risk'], color="#ff4b4b")

with col_bottom_right:
    st.subheader("Top 10 States by Charged-Off Principal ($)")
    top_states = state_df.head(10).set_index('state')['amount_at_risk']
    st.bar_chart(top_states)
