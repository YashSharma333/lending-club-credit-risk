import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load the hidden credentials
load_dotenv()

# 1. Configure the Web Page
st.set_page_config(page_title="Credit Risk Portfolio", layout="wide")
st.title("Institutional Credit Risk Analysis")
st.markdown("Analyzing 2.2M+ LendingClub records to identify default drivers and risk-adjusted returns.")

# 2. Database Connection (Cached so it doesn't reconnect on every click)
@st.cache_resource
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

engine = init_connection()

# 3. Data Loader
@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

st.divider()

# ==========================================
# UI SECTION 1: Risk-Adjusted Returns
# ==========================================
st.subheader("1. The Efficient Frontier: Risk-Adjusted ROI by Credit Grade")

roi_query = """
SELECT 
    grade,
    COUNT(loan_id) AS total_closed_loans,
    ROUND(((SUM(total_pymnt) - SUM(loan_amnt)) / SUM(loan_amnt)) * 100, 2) as roi_percentage
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
GROUP BY grade
ORDER BY grade ASC;
"""
df_roi = load_data(roi_query)

col1, col2 = st.columns(2)
with col1:
    st.dataframe(df_roi, use_container_width=True)
with col2:
    # Render a bar chart mapping grades to their ROI
    st.bar_chart(data=df_roi, x='grade', y='roi_percentage', color="#ff4b4b")

st.divider()

# ==========================================
# UI SECTION 2: Credit Utilization Warning
# ==========================================
st.subheader("2. Credit Utilization as an Early Warning Indicator")

util_query = """
SELECT 
    CASE 
        WHEN revol_util < 30 THEN '1. Low (<30%%)'
        WHEN revol_util BETWEEN 30 AND 60 THEN '2. Moderate (30-60%%)'
        WHEN revol_util BETWEEN 60 AND 90 THEN '3. High (60-90%%)'
        ELSE '4. Maxed Out (>90%%)'
    END AS utilization_bracket,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
  AND revol_util IS NOT NULL
GROUP BY utilization_bracket
ORDER BY utilization_bracket ASC;
"""
df_util = load_data(util_query)

col3, col4 = st.columns(2)
with col3:
    st.dataframe(df_util, use_container_width=True)
with col4:
    st.bar_chart(data=df_util, x='utilization_bracket', y='default_rate')