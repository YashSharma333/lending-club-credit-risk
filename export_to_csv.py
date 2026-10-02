import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine


# Load the hidden credentials
load_dotenv()

#Database Connection (Cached so it doesn't reconnect on every click)
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# Connect to your database
engine = init_connection()

# Your existing SQL queries
roi_query = """SELECT grade, COUNT(loan_id) AS total_closed_loans, ROUND(((SUM(total_pymnt) - SUM(loan_amnt)) / SUM(loan_amnt)) * 100, 2) as roi_percentage FROM loan_portfolio WHERE loan_status IN ('Fully Paid', 'Charged Off') GROUP BY grade ORDER BY grade ASC;"""

lgd_query = """SELECT grade, COUNT(loan_id) AS total_defaults, ROUND(AVG((loan_amnt - total_pymnt) / loan_amnt) * 100, 2) as avg_lgd_percentage, ROUND(AVG(recoveries / loan_amnt) * 100, 2) as recovery_rate_percentage FROM loan_portfolio WHERE loan_status = 'Charged Off' GROUP BY grade ORDER BY grade ASC;"""

matrix_query = """SELECT CASE WHEN fico_range_low >= 750 THEN '1. Excellent (750+)' WHEN fico_range_low >= 700 THEN '2. Good (700-749)' WHEN fico_range_low >= 660 THEN '3. Fair (660-699)' ELSE '4. Poor (<660)' END AS fico_bracket, CASE WHEN dti < 15 THEN '1. Low (<15%)' WHEN dti BETWEEN 15 AND 25 THEN '2. Moderate (15-25%)' ELSE '3. High (>25%)' END AS dti_bracket, ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate FROM loan_portfolio WHERE loan_status IN ('Fully Paid', 'Charged Off') AND fico_range_low IS NOT NULL AND dti IS NOT NULL GROUP BY fico_bracket, dti_bracket ORDER BY fico_bracket ASC, dti_bracket ASC;"""

util_query = """SELECT CASE WHEN revol_util < 30 THEN '1. Low (<30%%)' WHEN revol_util BETWEEN 30 AND 60 THEN '2. Moderate (30-60%%)' WHEN revol_util BETWEEN 60 AND 90 THEN '3. High (60-90%%)' ELSE '4. Maxed Out (>90%%)' END AS utilization_bracket, ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate FROM loan_portfolio WHERE loan_status IN ('Fully Paid', 'Charged Off') AND revol_util IS NOT NULL GROUP BY utilization_bracket ORDER BY utilization_bracket ASC;"""

# Write all queries to separate tabs in one Excel file
print("Exporting data to Excel...")
with pd.ExcelWriter('Credit_Risk_Portfolio.xlsx') as writer:
    pd.read_sql(roi_query, engine).to_excel(writer, sheet_name='ROI_Data', index=False)
    pd.read_sql(lgd_query, engine).to_excel(writer, sheet_name='LGD_Data', index=False)
    pd.read_sql(matrix_query, engine).to_excel(writer, sheet_name='FICO_DTI_Data', index=False)
    pd.read_sql(util_query, engine).to_excel(writer, sheet_name='Utilization_Data', index=False)

print("Export Complete! Check your folder for Credit_Risk_Portfolio.xlsx")