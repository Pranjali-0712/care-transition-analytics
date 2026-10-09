# Care Transition Efficiency & Placement Outcome Analytics

## Project purpose
An interactive Data Analytics project that reframes the UAC reporting dataset as a process-flow pipeline: **CBP custody -> HHS care -> sponsor discharge**.

## Requirements implemented
- Care Pipeline Flow Visualization
- Transfer Efficiency Ratio
- Discharge Effectiveness Index
- End-to-end Pipeline Throughput
- Backlog Accumulation Rate
- Outcome Stability Score
- Daily and monthly movement trends
- Bottleneck / accumulation-pressure detection
- Weekday vs weekend pattern analysis
- Month-over-month placement/discharge trend analysis
- Prolonged stagnation / pressure identification through cumulative backlog proxy
- Date-range selection
- Percentage/ratio vs volume metric toggle
- Threshold-based visual alerts
- Automated key findings
- Data-quality and methodology notes
- Filtered-data and monthly-summary downloads
- Research paper
- Executive summary

## Important methodology note
The source is aggregate reporting data. It does not contain individual case IDs or entry/transfer/discharge timestamps. Therefore, ratios such as Transfer Efficiency and Discharge Effectiveness are **flow indicators**, not exact waiting-time or processing-speed measurements.

### KPI definitions
- **Transfer Efficiency Ratio** = Transfers / CBP Custody x 100
- **Discharge Effectiveness** = Discharges / HHS Care x 100
- **Pipeline Throughput** = Discharges / Apprehensions x 100
- **Backlog Accumulation Rate** = (Apprehensions - Discharges) / Apprehensions x 100
- **Outcome Stability Score** = 100 x (1 - coefficient of variation of discharge effectiveness), clipped to 0-100

## Project structure
```text
care-transition-analytics/
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── runtime.txt
├── data/
├── src/
│   ├── metrics.py
│   ├── data_cleaning.py
│   └── analysis.py
├── outputs/
└── docs/
    ├── research_paper.docx
    └── executive_summary.docx
```

## Run locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Then open the Local URL shown by Streamlit, normally `http://localhost:8501`.
