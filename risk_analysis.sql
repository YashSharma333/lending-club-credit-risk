-- ==========================================
-- CASE 1: Risk-Adjusted Return (ROI) Analysis
-- ==========================================

SELECT
grade,
COUNT(loan_id) AS total_closed_loans,
ROUND(SUM(loan_amnt), 2) AS total_cap_dep,
ROUND(SUM(total_pymnt) - SUM(loan_amnt), 2) as net_return,
ROUND(((SUM(total_pymnt) - SUM(loan_amnt)) / SUM(loan_amnt)) * 100, 2) as roi_percentage
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
GROUP BY grade
ORDER BY grade ASC;

-- ==========================================
-- CASE 2: Loss Given Default (LGD) & Recovery
-- ==========================================

SELECT
grade,
COUNT(loan_id) AS total_defaults,
ROUND(AVG(loan_amnt), 2) AS avg_loan_amount,
ROUND(AVG((loan_amnt - total_pymnt) / loan_amnt) * 100, 2) as avg_lgd_percentage,
ROUND(AVG(recoveries / loan_amnt) * 100, 2) as recovery_rate_percentage
FROM loan_portfolio
WHERE loan_status = 'Charged Off'
GROUP BY grade
ORDER BY grade ASC;

-- ==========================================
-- CASE 3: Origination Vintage Analysis
-- ==========================================

SELECT
RIGHT(issue_d, 4) AS origination_year,
COUNT(loan_id) AS total_loans_issued,
SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS defaulted_loans,
ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS vintage_default_rate
FROM loan_portfolio
WHERE issue_d IS NOT NULL
GROUP BY RIGHT(issue_d, 4)
ORDER BY origination_year ASC;

-- ==========================================
-- CASE 4: The "Capacity vs. Character" Matrix (FICO vs DTI)
-- ==========================================

SELECT
CASE
WHEN fico_range_low >= 750 THEN '1. Excellent (750+)'
WHEN fico_range_low >= 700 THEN '2. Good (700-749)'
WHEN fico_range_low >= 660 THEN '3. Fair (660-699)'
ELSE '4. Poor (<660)'
END AS fico_bracket,
CASE
WHEN dti < 15 THEN '1. Low (<15%)'
WHEN dti BETWEEN 15 AND 25 THEN '2. Moderate (15-25%)'
ELSE '3. High (>25%)'
END AS dti_bracket,
COUNT(loan_id) AS total_loans,
ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
AND fico_range_low IS NOT NULL
AND dti IS NOT NULL
GROUP BY fico_bracket, dti_bracket
ORDER BY fico_bracket ASC, dti_bracket ASC;

-- ==========================================
-- CASE 5: Credit Utilization as an Early Warning Indicator
-- ==========================================

SELECT
CASE
WHEN revol_util < 30 THEN '1. Low (<30%)'
WHEN revol_util BETWEEN 30 AND 60 THEN '2. Moderate (30-60%)'
WHEN revol_util BETWEEN 60 AND 90 THEN '3. High (60-90%)'
ELSE '4. Maxed Out (>90%)'
END AS utilization_bracket,
COUNT(loan_id) AS total_loans,
ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
AND revol_util IS NOT NULL
GROUP BY utilization_bracket
ORDER BY utilization_bracket ASC; 
