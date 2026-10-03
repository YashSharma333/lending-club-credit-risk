import os
import time
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def init_connection():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    return create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

def run_ingestion():
    engine = init_connection()
    csv_file_path = "accepted_2007_to_2018Q4.csv"
    
    # Master Schema Mapping
    column_mapping = {
        'id': 'loan_id',
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
        'addr_state': 'addr_state',
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

    columns_to_keep = list(column_mapping.keys())

    print("Initiating data pipeline...")
    # This line proves the file saved correctly and Python sees the new column
    print(f"VERIFICATION - Columns being loaded: {columns_to_keep}")
    
    start_time = time.time()
    chunk_size = 50000
    total_processed = 0
    first_chunk = True 

    for chunk in pd.read_csv(csv_file_path, usecols=columns_to_keep, chunksize=chunk_size, low_memory=False):
        
        chunk = chunk.rename(columns=column_mapping)
        chunk = chunk.dropna(subset=['loan_status'])
        
        if first_chunk:
            chunk.to_sql(name='loan_portfolio', con=engine, if_exists='replace', index=False)
            first_chunk = False
        else:
            chunk.to_sql(name='loan_portfolio', con=engine, if_exists='append', index=False)
            
        total_processed += len(chunk)
        print(f"Successfully loaded {total_processed:,} rows into MySQL...")

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)
    print(f"\nPipeline Complete! {total_processed:,} rows ingested.")
    print(f"Execution Time: {execution_time} seconds")

if __name__ == "__main__":
    run_ingestion()