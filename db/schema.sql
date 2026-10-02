USE credit_risk_db;

DROP TABLE IF EXISTS loan_portfolio;

CREATE TABLE IF NOT EXISTS loan_portfolio (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_amnt DECIMAL(12, 2),
    term VARCHAR(20),
    int_rate DECIMAL(7, 4),
    installment DECIMAL(10, 2),
    grade VARCHAR(5),
    sub_grade VARCHAR(5),
    emp_length VARCHAR(25),
    home_ownership VARCHAR(20),
    annual_inc DECIMAL(15, 2),
    verification_status VARCHAR(255),
    issue_d VARCHAR(20),
    loan_status VARCHAR(100),
    purpose VARCHAR(255),
    dti DECIMAL(10, 4),
    delinq_2yrs INT,
    fico_range_low INT,
    fico_range_high INT,
    inq_last_6mths INT,
    revol_bal DECIMAL(15, 2),
    revol_util DECIMAL(10, 4),
    total_pymnt DECIMAL(15, 2),
    recoveries DECIMAL(12, 2),
    last_pymnt_d VARCHAR(20)
);