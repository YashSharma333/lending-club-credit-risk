import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

# Load the hidden credentials
load_dotenv()

# Database Connection (Cached so it doesn't reconnect on every click)
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# Connect to your database
engine = init_connection()

# 1. Open and read your master SQL file
print("Reading SQL queries from risk_analysis.sql...")
with open('risk_analysis.sql', 'r') as file:
    sql_script = file.read()

# 2. Split the file into individual queries using the semicolon
# The list comprehension ensures we ignore any blank spaces at the end of the file
queries = [q.strip() for q in sql_script.split(';') if q.strip()]

# SAFETY CHECK: Ensure Python found all 10 queries
print(f"Found {len(queries)} queries.")

if len(queries) < 10:
    print("WARNING: Python did not find all 10 queries. Check your SQL file and ensure every query ends with a semicolon (;)")
else:
    # 3. Write to Excel using the dynamically loaded queries
    print("Exporting complete 10-query dashboard data to Excel...")
    
    with pd.ExcelWriter('Credit_Risk_Master.xlsx') as writer:
        # Original Thesis Data
        pd.read_sql(queries[0], engine).to_excel(writer, sheet_name='Top_KPIs', index=False)
        pd.read_sql(queries[1], engine).to_excel(writer, sheet_name='ROI_Data', index=False)
        pd.read_sql(queries[2], engine).to_excel(writer, sheet_name='LGD_Data', index=False)
        pd.read_sql(queries[3], engine).to_excel(writer, sheet_name='FICO_DTI_Data', index=False)
        pd.read_sql(queries[4], engine).to_excel(writer, sheet_name='Utilization_Data', index=False)
        
        # New BI Dashboard Data
        pd.read_sql(queries[5], engine).to_excel(writer, sheet_name='Term_Data', index=False)
        pd.read_sql(queries[6], engine).to_excel(writer, sheet_name='Emp_Length_Data', index=False)
        pd.read_sql(queries[7], engine).to_excel(writer, sheet_name='Purpose_Data', index=False)
        pd.read_sql(queries[8], engine).to_excel(writer, sheet_name='Loan_Amount_Data', index=False)
        pd.read_sql(queries[9], engine).to_excel(writer, sheet_name='State_Data', index=False)

    print("Export Complete! Check your folder for Credit_Risk_Master.xlsx")