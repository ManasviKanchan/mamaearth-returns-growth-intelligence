# Mamaearth Returns & Growth Intelligence

An end-to-end retail analytics capstone project using **SQL, Python, data visualization, and Generative AI** to investigate revenue performance, customer returns, data quality, and operational risks.

## Project Objectives

- Build a relational SQL database for retail transactions.
- Analyze revenue, return patterns, and payment-method performance.
- Clean duplicate records and investigate unusual order quantities.
- Create visualizations highlighting revenue trends and return risks.
- Generate a business narrative using Google's Gemini API.
- Provide a deterministic offline narrative when the API is unavailable.

## Project Structure

```text
mamaearth-returns-growth-intelligence/
├── data/
│   └── CSV datasets
├── sql/
│   ├── schema.sql
│   ├── seed_data.sql
│   └── reports.sql
├── analysis/
│   ├── clean_and_eda.py
│   └── visualize.py
├── visualizations/
│   ├── monthly_revenue_trend.png
│   └── return_rate_by_payment.png
├── narrator/
│   ├── findings.json
│   ├── generate_narrative.py
│   └── sample_output.txt
└── README.md
```

## Part 1: SQL Database and Reporting

The SQL component establishes the relational database and provides queries for business reporting.

**Execution order:**

1. `sql/schema.sql` — Creates the required database tables.
2. `sql/seed_data.sql` — Populates the tables with project data.
3. `sql/reports.sql` — Runs SQL reports and analytical queries.

Execute these scripts in order using a compatible SQL environment.

### Raw Dataset Summary

| Metric | Value |
|---|---:|
| Raw orders | 180 |
| Customers | 45 |
| Products | 16 |
| Raw revenue | ₹99,860.20 |

## Part 2: Python Data Cleaning, EDA and Visualization

### Data Cleaning and Exploratory Analysis

Script: `analysis/clean_and_eda.py`

The analysis includes:

- Removing duplicate orders.
- Calculating cleaned revenue.
- Analyzing returns by payment method.
- Identifying high-risk payment and city-tier combinations.
- Detecting unusually large order quantities.
- Comparing apparent and outlier-corrected monthly revenue.

The script also exports structured findings to `narrator/findings.json`, allowing the narrative generator to use verified analytical results.

### Key Findings

| Metric | Result |
|---|---:|
| Cleaned orders | 175 |
| Duplicate orders removed | 5 |
| Cleaned revenue | ₹97,358.30 |
| Duplicate revenue reconciliation | ₹2,501.90 |
| COD return rate | 44.4% |
| CARD return rate | 14.7% |
| UPI return rate | 18.9% |
| COD Tier-2 return rate | 54.5% |
| True peak month after outlier adjustment | March 2026 |
| True peak month revenue | ₹20,318.90 |

January 2026 initially showed revenue of ₹29,582.10. After excluding flagged quantity outliers from the monthly trend, its revenue was ₹11,637.10.

These findings indicate patterns worth investigating; they do not establish causal relationships.

### Visualizations

Script: `analysis/visualize.py`

The project generates:

- `visualizations/monthly_revenue_trend.png`
- `visualizations/return_rate_by_payment.png`

These charts illustrate monthly revenue performance and differences in return rates across payment methods.

## Part 3: Generative AI Business Narrative

Script: `narrator/generate_narrative.py`

The narrative generator uses the **Situation–Complication–Resolution (SCR)** framework to translate analytical findings into a report for regional operations and finance stakeholders.

### Online Gemini Generation

The generator uses:

- Google GenAI Python SDK (`google-genai`)
- Gemini model: `gemini-flash-lite-latest`
- Temperature: `0.0`
- Maximum output tokens: `1200`
- API timeout: `30000` milliseconds

The API key is accessed through the `GEMINI_API_KEY` environment variable. It is not stored in the GitHub repository.

### Offline Fallback

If the API key is missing or the Gemini request fails, the generator uses `generate_scr_narrative_offline(findings)`.

This deterministic fallback:

- Requires no internet connection.
- Uses the same verified findings.
- Produces Situation, Complication, and Resolution sections.
- Allows the project to run without a Gemini API key.

### Numeric Accuracy Validation

The generator checks five critical findings:

1. Cleaned revenue: ₹97,358.30
2. COD return rate: 44.4%
3. COD Tier-2 return rate: 54.5%
4. Duplicate reconciliation: ₹2,501.90
5. True peak month: March 2026, ₹20,318.90

Each check prints `PASS` or `FAIL`. If Gemini's narrative fails validation, the script switches to the offline narrative.

A Gemini-generated narrative was successfully tested, and all five numeric checks passed. A reviewed version is saved in `narrator/sample_output.txt`.

## Reproducing the Project

### 1. Clone the Repository

```bash
git clone https://github.com/ManasviKanchan/mamaearth-returns-growth-intelligence.git
cd mamaearth-returns-growth-intelligence
```

### 2. Install Python Dependencies

```bash
pip install pandas numpy matplotlib seaborn google-genai
```

### 3. Run the SQL Scripts

In your SQL environment, execute the files in this order:

```text
sql/schema.sql
sql/seed_data.sql
sql/reports.sql
```

### 4. Run Data Cleaning and EDA

```bash
python analysis/clean_and_eda.py
```

This step performs data analysis and generates or updates `narrator/findings.json`.

### 5. Generate Visualizations

```bash
python analysis/visualize.py
```

Generated charts are saved in the `visualizations/` folder.

### 6. Generate the Business Narrative

**Option A: Online generation with Gemini**

Set the `GEMINI_API_KEY` environment variable securely before running the script.

In Google Colab, store the key in Secrets under `GEMINI_API_KEY` and enable notebook access. Then run:

```python
import os
from google.colab import userdata

os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")

!python narrator/generate_narrative.py
```

**Option B: Offline generation**

Run without setting `GEMINI_API_KEY`:

```bash
python narrator/generate_narrative.py
```

The script automatically uses the offline fallback and saves the resulting narrative to `narrator/sample_output.txt`.

**Note:** Running the generator overwrites the existing sample output file.

## Business Recommendations

- Investigate elevated COD return rates, particularly in Tier-2 cities.
- Review possible operational reasons for differences in return rates before changing policies.
- Reconcile duplicate transactions before publishing revenue reports.
- Examine flagged quantity outliers when interpreting monthly performance.
- Use validated analytical findings to support regional operational decisions.

## Technologies Used

- **SQL:** Database design, data loading, and reporting
- **Python:** Data cleaning and exploratory analysis
- **Pandas and NumPy:** Data manipulation and calculations
- **Matplotlib and Seaborn:** Data visualization
- **Google Gemini API:** AI-assisted business narrative generation
- **GitHub:** Version control and project submission

## Conclusion

This capstone demonstrates a complete analytics workflow, from structured retail data and SQL reporting to Python-based analysis, visualizations, and AI-assisted business communication.

The project emphasizes reproducibility, numerical validation, transparent data cleaning, and responsible interpretation of business findings.
