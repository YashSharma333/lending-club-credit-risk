-- ==========================================
-- 1. Top Ribbon KPIs (Total Borrowers, Volume, Charged-Off Principal, Default Rate)
-- ==========================================
SELECT 
    COUNT(loan_id) AS total_borrowers,
    SUM(loan_amnt) AS total_loan_amount,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN loan_amnt ELSE 0 END) AS amount_at_risk,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS overall_default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off');

-- ==========================================
-- 2. Risk-Adjusted Return (ROI) Analysis
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
-- 3. Loss Given Default (LGD) & Recovery
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
-- 4. The "Capacity vs. Character" Matrix (FICO vs DTI)
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
-- 5. Credit Utilization as an Early Warning Indicator
--    (chart default_rate as a COLUMN chart, total_defaults is for share-of-defaults views)
-- ==========================================
SELECT 
    CASE 
        WHEN revol_util < 30 THEN '1. Low (<30%)'
        WHEN revol_util BETWEEN 30 AND 60 THEN '2. Moderate (30-60%)'
        WHEN revol_util BETWEEN 60 AND 90 THEN '3. High (60-90%)'
        ELSE '4. Maxed Out (>90%)'
    END AS utilization_bracket,
    COUNT(loan_id) AS total_loans,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS total_defaults,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
  AND revol_util IS NOT NULL
GROUP BY utilization_bracket
ORDER BY utilization_bracket ASC;

-- ==========================================
-- 6. Default Loans by Term Month (36 vs 60)
--    (doughnut: total_defaults = share of all defaults by term)
-- ==========================================
SELECT 
    term,
    COUNT(loan_id) AS total_loans,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS total_defaults,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off') AND term IS NOT NULL
GROUP BY term
ORDER BY term;

-- ==========================================
-- 7. Employment Length Risk
--    (doughnut: total_defaults = share of all defaults by employment length)
-- ==========================================
SELECT 
    CASE 
        WHEN emp_length IN ('< 1 year', '1 year') THEN '1. Junior (<2 yrs)'
        WHEN emp_length IN ('2 years', '3 years', '4 years', '5 years') THEN '2. Mid (2-5 yrs)'
        WHEN emp_length IN ('6 years', '7 years', '8 years', '9 years') THEN '3. Senior (6-9 yrs)'
        WHEN emp_length = '10+ years' THEN '4. Veteran (10+ yrs)'
        ELSE '5. Unknown'
    END AS employment_duration,
    COUNT(loan_id) AS total_loans,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS total_defaults,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
GROUP BY employment_duration
ORDER BY employment_duration;

-- ==========================================
-- 8. Loan Default Rate by Purpose
--    (top 8 purposes by volume, chart default_rate as a sorted BAR chart)
-- ==========================================
SELECT 
    purpose,
    COUNT(loan_id) AS total_loans,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) AS total_defaults,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off') AND purpose IS NOT NULL
GROUP BY purpose
ORDER BY total_loans DESC
LIMIT 8;

-- ==========================================
-- 9. Amount at Risk & Default Rate by Loan Amount
-- ==========================================
SELECT 
    CASE 
        WHEN loan_amnt <= 8000 THEN '1. $0-$8k'
        WHEN loan_amnt <= 16000 THEN '2. $8k-$16k'
        WHEN loan_amnt <= 24000 THEN '3. $16k-$24k'
        WHEN loan_amnt <= 32000 THEN '4. $24k-$32k'
        ELSE '5. $32k+'
    END AS loan_amount_bin,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN loan_amnt ELSE 0 END) AS amount_at_risk,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off')
GROUP BY loan_amount_bin
ORDER BY loan_amount_bin;

-- ==========================================
-- 10. Amount at Risk by State (Geographic Map)
-- ==========================================
SELECT 
    addr_state AS state,
    SUM(CASE WHEN loan_status = 'Charged Off' THEN loan_amnt ELSE 0 END) AS amount_at_risk,
    ROUND((SUM(CASE WHEN loan_status = 'Charged Off' THEN 1 ELSE 0 END) / COUNT(loan_id)) * 100, 2) AS default_rate
FROM loan_portfolio
WHERE loan_status IN ('Fully Paid', 'Charged Off') AND addr_state IS NOT NULL
GROUP BY addr_state
ORDER BY amount_at_risk DESC;
