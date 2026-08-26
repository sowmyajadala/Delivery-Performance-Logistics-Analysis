# Delivery Performance, Delay Risk & Logistics Efficiency Analysis

A complete data-analysis and Streamlit dashboard project for **global supply-chain delivery diagnostics** using the APL Logistics dataset.

## Project Objective

The project evaluates delivery performance, late-delivery risk, shipping-mode efficiency, regional risk concentration, and customer-segment exposure so logistics teams can move from reactive issue handling to data-driven operational control.

## Dataset

- File: `data/APL_Logistics.csv`
- Rows: 180,519
- Columns: 40
- Encoding: Latin-1 (`latin1`)

Key fields include:

- `Days for shipping (real)`
- `Days for shipment (scheduled)`
- `Delivery Status`
- `Late_delivery_risk`
- `Shipping Mode`
- `Market`
- `Order Region`
- `Order Country`
- `Customer Segment`
- Sales and profit fields

> **Dataset limitation:** the supplied CSV contains no date field. The Streamlit app includes date-filter logic that activates automatically if a compatible dated version of the dataset is later supplied.

## Derived Fields

### Delivery Gap (Days)

```text
Delivery Gap = Actual Shipping Days - Scheduled Shipping Days
```

Positive values indicate delivery beyond the scheduled shipping duration.

### On-Time Flag

```text
On Time Flag = 1 when Late_delivery_risk = 0, otherwise 0
```

## Key Performance Indicators

1. **On-Time Delivery Rate (%)** - percentage of orders without late-delivery risk.
2. **Average Delivery Gap (Days)** - mean difference between actual and scheduled shipping days.
3. **Late Delivery Risk Ratio (%)** - proportion of records flagged as late-delivery risk.
4. **Shipping Mode Efficiency Index** - SLA compliance percentage for the selected data.
5. **Regional Delay Index** - mean delivery gap for the selected region/market selection.

## Overall Results

- Total records analyzed: **180,519**
- On-Time Delivery Rate: **45.17%**
- Late Delivery Risk Ratio: **54.83%**
- Average Delivery Gap: **0.57 days**
- Average delay among positive-delay orders: **1.62 days**

### Shipping Mode Performance

| Shipping Mode | Orders | Late Risk % | Avg Delivery Gap | SLA Compliance % |
|---|---:|---:|---:|---:|
| Standard Class | 107,752 | 38.07 | -0.00 | 61.93 |
| Same Day | 9,737 | 45.74 | 0.48 | 54.26 |
| Second Class | 35,216 | 76.63 | 1.99 | 23.37 |
| First Class | 27,814 | 95.32 | 1.00 | 4.68 |

## Dashboard Modules

- Delivery Performance Overview
- Delay Risk Analysis Dashboard
- Shipping Mode Comparison
- Regional & Market Diagnostics
- Market × Region Heatmap
- Geographic late-risk choropleth
- Customer Segment Impact Analysis
- Interactive filters for shipping mode, market, region, and customer segment
- Automatic date-range selector when a date field is available

## Run Locally

1. Open this project folder in VS Code.
2. Open a terminal in the project folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Push this complete folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the main file path to `app.py`.
5. Deploy.

## Submission Files Included

- `app.py` - Streamlit dashboard
- `analysis.ipynb` - end-to-end exploratory analysis
- `requirements.txt` - deployment dependencies
- `report/Research_Paper_Delivery_Performance.pdf` - research-paper-style EDA report
- `report/Executive_Summary.pdf` - short stakeholder summary
- `video_demo_script.txt` - recording script for the project demo

## Recommended Operational Actions

- Investigate First Class and Second Class scheduling assumptions because they show the highest late-risk ratios.
- Use Standard Class performance as a benchmark for SLA-compliance practices.
- Monitor high-risk regions through a recurring regional delay scorecard.
- Introduce exception alerts when delivery gap exceeds SLA tolerance.
- Segment monitoring by customer type so high-value or contract-sensitive customers can receive proactive intervention.
