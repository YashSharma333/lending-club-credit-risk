-- ---------------------------------------------------------
-- Portfolio Risk Analysis Database Schema
-- Run once:  mysql -u <user> -p < sql/01_schema.sql
-- WARNING: this drops and recreates loan_portfolio (any loaded data is lost).
-- ---------------------------------------------------------

CREATE DATABASE IF NOT EXISTS lending_portfolio;
USE lending_portfolio;

DROP TABLE IF EXISTS loan_portfolio;

CREATE TABLE loan_portfolio (
    loan_id VARCHAR(50) PRIMARY KEY,
    loan_amnt DECIMAL(15, 2),
    term VARCHAR(20),
    int_rate DECIMAL(5, 2),
    installment DECIMAL(10, 2),
    grade VARCHAR(5),
    sub_grade VARCHAR(5),
    emp_length VARCHAR(20),
    home_ownership VARCHAR(20),
    annual_inc DECIMAL(15, 2),
    verification_status VARCHAR(50),
    issue_d VARCHAR(20),
    loan_status VARCHAR(100),   -- was 50: "Does not meet the credit policy. Status:Charged Off" is 51 chars
    purpose VARCHAR(50),
    addr_state VARCHAR(5),
    dti DECIMAL(10, 2),
    delinq_2yrs INT,
    fico_range_low INT,
    fico_range_high INT,
    inq_last_6mths INT,
    revol_bal DECIMAL(15, 2),
    revol_util DECIMAL(10, 2),
    total_pymnt DECIMAL(15, 2),
    recoveries DECIMAL(15, 2),
    last_pymnt_d VARCHAR(20)
);

-- Every analysis query filters on loan_status, most also group by grade.
CREATE INDEX idx_status_grade ON loan_portfolio (loan_status, grade);
