import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import time

load_dotenv()


# 1. Database Credentials (Update your password)
def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
# Create the connection engine
engine = init_connection()

# 2. File Path
csv_file_path = "/Users/yashsharma/Documents/lending_portfolio_model/accepted_2007_to_2018Q4.csv"

# 3. Column Mapping
column_mapping = {
    'loan_amnt': 'loan_amnt',
    'term': 'term',
    'int_rate': 'int_rate',
    'installment': 'installment',
    'grade': 'grade',
    'sub_grade': 'sub_grade',
    'emp_length': 'emp_length',
    'home_ownership': 'home_ownership',
    'annual_inc': 'annual_inc',
    'verification_status': 'verification_status',
    'issue_d': 'issue_d',
    'loan_status': 'loan_status',
    'purpose': 'purpose',
    'dti': 'dti',
    'delinq_2yrs': 'delinq_2yrs',
    'fico_range_low': 'fico_range_low',
    'fico_range_high': 'fico_range_high',
    'inq_last_6mths': 'inq_last_6mths',
    'revol_bal': 'revol_bal',
    'revol_util': 'revol_util',
    'total_pymnt': 'total_pymnt',
    'recoveries': 'recoveries',
    'last_pymnt_d': 'last_pymnt_d'
}

print("Starting batch ingestion...")
start_time = time.time()
total_rows = 0
chunk_size = 500000 # Process 50,000 rows at a time

try:
    for chunk in pd.read_csv(csv_file_path, chunksize= chunk_size, low_memory=False):
        chunk = chunk[[col for col in column_mapping.keys() if col in chunk.columns]]
        chunk = chunk.rename(columns= column_mapping)

        chunk.to_sql(name='loan_portfolio', con=engine, if_exists='append', index=False)

        total_rows += len(chunk)
        print(f"Successfully inserted {total_rows} rows...")

    end_time = time.time()
    print(f"Ingestion Complete! {total_rows} rows processed in {round(end_time - start_time, 2)} seconds.")

except Exception as e:
    print(f"An error occurred: {e}")
