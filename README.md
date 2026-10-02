# Institutional Credit Risk & Yield Analysis

## Project Overview
An end-to-end data engineering and risk analysis pipeline built to evaluate a 2.2 million-row LendingClub loan portfolio. This project moves beyond basic data visualization to identify the underlying drivers of subprime loan defaults and calculate actual risk-adjusted returns (ROI). 

**Author:** Yash Sharma

## Technical Architecture
* **Data Engineering (Python & Pandas):** Built a batch-processing ingestion pipeline (`ingest_data.py`) to process 2.2M+ rows (2GB+ CSV) in memory-safe 50,000-row chunks, bypassing local RAM limitations.
* **Database (MySQL & SQLAlchemy):** Designed the relational schema and sanitized raw data to eliminate trailing artifacts and phantom records for accurate downstream aggregations.
* **Analytics (SQL):** Authored a master SQL script to evaluate five distinct credit risk business cases, including Loss Given Default (LGD) and FICO vs. Debt-to-Income risk matrices.
* **Presentation Layer (Streamlit):** Developed an interactive local web application to visualize the Efficient Frontier and early warning default indicators dynamically.
* **Reporting (OpenPyXL):** Automated the extraction of aggregated SQL views into a multi-tab Excel workbook for executive dashboarding.

## Key Business Findings
1. **Subprime Yield Inversion:** Despite carrying higher interest rates, Grades E, F, and G generated negative ROI (down to -8.77%).
2. **Loss Given Default (LGD):** The negative yield curve is driven by a rigid ~45-50% principal loss rate on defaults, compounded by single-digit third-party recovery rates.
3. **Capacity Out-Predicts Character:** Highly leveraged borrowers (DTI >25%) with "Excellent" FICO scores (750+) defaulted at a higher rate (13.12%) than low-DTI borrowers with merely "Good" FICO scores (12.62%). 
4. **Early Warning Indicators:** Borrowers maxing out existing revolving credit (>90% utilization) prior to origination defaulted at 23.32%, signaling that strict utilization caps should be automated in underwriting.

## How to Run Locally
1. Clone the repository.
2. Install the required dependencies: `pip install -r requirements.txt`
3. Create a `.env` file in the root directory with your MySQL credentials (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_NAME`).
4. Run the schema creation script in your SQL environment.
5. Execute the pipeline: `python src/ingest_data.py`
6. Launch the dashboard: `streamlit run dashboard.py`