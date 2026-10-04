import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import re 

# 1. Page Configuration (Wide layout for BI Dashboard)
st.set_page_config(page_title="Credit Risk Dashboard", layout="wide")
st.title("Portfolio Risk & Yield Analysis")
st.markdown("### 2007-2018 Originations")

load_dotenv()

# 2. Database Connection (Cached)
@st.cache_resource
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

engine = init_connection()

# 3. Data Loading (Cached to prevent re-running SQL on every click)
@st.cache_data
def load_data():
    with open('risk_analysis.sql', 'r') as file:
        sql_script = file.read()
    
    # Split by semicolon and remove empty strings
    queries = [q.strip() for q in sql_script.split(';') if q.strip()]
    
    dfs = []
    for query in queries:
        # Strip single-line (--) and multi-line (/* */) comments temporarily for the check
        clean_query = re.sub(r'--.*', '', query).strip()
        clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL).strip()
        
        # Check if the actual SQL code starts with SELECT or WITH
        if clean_query.upper().startswith(("SELECT", "WITH")):
            # Execute the original query against the database
            dfs.append(pd.read_sql(query, engine))
            
    return dfs

# Load the dataframes
try:
    data = load_data()
    kpi_df, roi_df, lgd_df, fico_dti_df, utilization_df, term_df, emp_length_df, purpose_df, loan_amount_df, state_df = data
except Exception as e:
    st.error(f"Error loading data. Check your SQL file. Details: {e}")
    st.stop()


# ==========================================
# DASHBOARD LAYOUT & VISUALS
# ==========================================

# ROW 1: Top KPI Ribbon
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Borrowers", f"{kpi_df['total_borrowers'].iloc[0]:,}")
with col2:
    st.metric("Total Loan Volume", f"${kpi_df['total_loan_amount'].iloc[0]:,.0f}")
with col3:
    st.metric("Capital at Risk", f"${kpi_df['amount_at_risk'].iloc[0]:,.0f}")
with col4:
    st.metric("Portfolio Default Rate", f"{kpi_df['overall_default_rate'].iloc[0]}%")

st.markdown("---")

# ROW 2: Demographics & Term Risk
col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.subheader("Default Volume by Term")
    st.bar_chart(data=term_df.set_index('term')['total_defaults'], color="#ff4b4b")

with col_mid:
    st.subheader("Risk by Employment Length")
    st.bar_chart(data=emp_length_df.set_index('employment_duration')['default_rate'])

with col_right:
    st.subheader("Top Risk by Loan Purpose")
    st.dataframe(purpose_df[['purpose', 'default_rate']], hide_index=True, use_container_width=True)

st.markdown("---")

# ROW 3: Geographic & Bracket Risk
col_bottom_left, col_bottom_right = st.columns(2)

with col_bottom_left:
    st.subheader("Amount at Risk by Loan Bracket")
    st.bar_chart(data=loan_amount_df.set_index('loan_amount_bin')['amount_at_risk'], color="#ff4b4b")

with col_bottom_right:
    st.subheader("Top 10 Highest Risk States")
    # Sort and take top 10 for clean visualization
    top_states = state_df.head(10).set_index('state')['amount_at_risk']
    st.bar_chart(top_states)