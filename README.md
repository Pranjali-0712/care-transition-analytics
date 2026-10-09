# Care Transition Efficiency & Placement Outcome Analytics

### An Interactive Data Analytics Dashboard for Operational Flow, Workload Trends, and Bottleneck Exploration

<p align="center">
  <strong>Python | Pandas | NumPy | Plotly | Streamlit</strong>
</p>

<p align="center">
  <a href="https://pranjali-0712-care-transition-analytics-app-dskbox.streamlit.app/">
    <strong>🚀 View Live Dashboard</strong>
  </a>
  &nbsp; | &nbsp;
  <a href="https://github.com/Pranjali-0712/care-transition-analytics">
    <strong>💻 View Source Code</strong>
  </a>
</p>

---

## 📌 Project Overview

Care Transition Efficiency & Placement Outcome Analytics is an interactive data analytics project designed to explore aggregate reporting data associated with the unaccompanied children care pipeline in the United States.

The dashboard organizes reported measures relating to apprehension, transfers, care workload, and discharges into an interactive interface. It helps users explore reporting trends, compare operational indicators, identify unusual patterns, and investigate potential pressure points.

Built with Python, Pandas, NumPy, Plotly, and Streamlit, the application combines data preparation, analytical calculations, and interactive visualizations in a single web-based dashboard.

**Project focus:** Descriptive analytics, operational reporting, trend visualization, and transparent interpretation of aggregate data.

## 🎯 Problem Statement

Operational datasets often contain multiple measures representing different stages of a process. When these measures are difficult to compare, identifying trends and potential operational bottlenecks becomes challenging.

This project addresses that challenge by providing a centralized dashboard to:

- Explore aggregate operational activity over time.
- Compare reported inflows, transfers, care workload, and discharges.
- Analyze monthly and day-of-week patterns.
- Highlight reporting periods that may require further investigation.
- Communicate analytical findings while acknowledging data limitations.

## 🎯 Project Objectives

- Clean and prepare aggregate reporting data for analysis.
- Calculate descriptive flow and workload indicators.
- Visualize trends across a selected reporting period.
- Compare reporting patterns across weekdays and weekends.
- Identify potential bottlenecks and unusual reporting patterns.
- Provide interactive filters and downloadable analytical results.
- Present findings through a user-friendly web dashboard.

## ✨ Key Features

### 📊 Interactive KPI Dashboard
Summarizes selected reporting measures and calculated indicators for the chosen date range.

### 📈 Trend Analysis
Visualizes changes in reported activity over time and supports exploration of monthly patterns.

### 🔄 Flow and Workload Analysis
Examines reported apprehensions, transfers, care workload, and discharges using descriptive aggregate indicators.

### 🚦 Potential Bottleneck Indicators
Highlights selected patterns or reporting periods that may warrant additional investigation.

### 📅 Date-Range Filtering
Allows users to explore a specific reporting period and update the dashboard's analytical views.

### 📆 Weekday and Weekend Comparison
Supports comparison of aggregate reporting patterns across different days of the week.

### 📉 Volume and Ratio Views
Allows exploration of reporting volumes and selected calculated ratios, where supported by the dashboard.

### 📥 Downloadable Results
Provides access to analytical outputs through the dashboard's available download options.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data cleaning, transformation, and aggregation |
| NumPy | Numerical calculations and analytical operations |
| Plotly | Interactive charts and visualizations |
| Streamlit | Interactive dashboard and web application |
| Git | Version control |
| GitHub | Source-code hosting |
| Streamlit Community Cloud | Application deployment |

## 🔄 Project Workflow

1. **Data Ingestion**  
   Load the available aggregate reporting dataset.

2. **Data Cleaning**  
   Identify and handle blank or invalid records and prepare data for analysis.

3. **Data Transformation**  
   Standardize the reporting fields and prepare data for aggregation.

4. **Metric Calculation**  
   Calculate descriptive indicators based on the available aggregate measures.

5. **Exploratory Analysis**  
   Examine changes over time, workload patterns, and differences between reporting periods.

6. **Data Visualization**  
   Present findings through interactive charts, summary indicators, and tables.

7. **Dashboard Deployment**  
   Deploy the Streamlit application for browser-based access.

## 📐 Analytical Methodology

The dashboard uses aggregate reporting measures to explore activity across the available stages of the care pipeline.

Depending on the selected reporting period and the metrics displayed by the application, the analysis may include:

- Total reported apprehensions, transfers, and discharges.
- Reported care workload.
- Monthly reporting trends.
- Weekday and weekend comparisons.
- Transfer and discharge flow indicators.
- Differences between selected inflow and outflow measures.
- Exploratory indicators of reporting consistency or imbalance.

### Important Interpretation Notes

The dataset contains aggregate reporting counts rather than individual-level records linked across stages.

Therefore:

- Transfers and discharges cannot be matched to specific individuals.
- The dashboard does not calculate individual waiting times.
- Aggregate ratios must not be interpreted automatically as individual success probabilities.
- A difference between inflow and outflow totals is not necessarily a direct measurement of actual backlog.
- Exploratory consistency indicators are not independently validated measures of placement quality.

The dashboard is intended for descriptive exploration, not individual case assessment, causal inference, or policy evaluation.

## 📂 Project Structure

```text
care-transition-analytics/
│
├── app.py
├── requirements.txt
├── README.md
├── Procfile
├── runtime.txt
├── .gitignore
│
├── data/
│   └── HHS_Unaccompanied_Alien_Children_Program.csv
│
├── src/
│   ├── analysis.py
│   ├── data_cleaning.py
│   └── metrics.py
│
├── docs/
│   ├── research_paper.docx
│   └── executive_summary.docx
│
└── outputs/
    ├── cleaned_care_transition_data.csv
    ├── monthly_summary.csv
    └── charts/
```

*Note: The structure above describes the intended project layout. Files excluded from version control, including datasets and generated outputs, may not appear in the public GitHub repository.*

## 🚀 Live Demo

Explore the deployed dashboard:

**[Open Care Transition Analytics Dashboard](https://pranjali-0712-care-transition-analytics-app-dskbox.streamlit.app/)**

The dashboard can be accessed through a web browser without installing the project locally.

## 💻 GitHub Repository

Source code and project documentation:

**[Pranjali-0712/care-transition-analytics](https://github.com/Pranjali-0712/care-transition-analytics)**

## ⚙️ Installation and Local Setup

Follow these steps to run the project on your computer.

### Prerequisites

- Python 3.11 or another version compatible with the dependencies.
- Git.
- A terminal or code editor such as Visual Studio Code.

### 1. Clone the repository

```bash
git clone https://github.com/Pranjali-0712/care-transition-analytics.git
```

### 2. Navigate to the project directory

```bash
cd care-transition-analytics
```

### 3. Create a virtual environment

**Windows:**

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the dataset

Place the authorized dataset at the path expected by the application:

```text
data/HHS_Unaccompanied_Alien_Children_Program.csv
```

The original dataset may not be included in the public repository. Obtain it from an authorized source and follow its applicable sharing and usage conditions.

### 6. Run the dashboard

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser to access the dashboard.

## 📊 Dataset and Data Quality

The analysis was developed using aggregate reporting data associated with the unaccompanied children care pipeline.

The currently analyzed dataset contains:

- **720 populated reporting records** after blank or invalid rows are excluded.
- **Reporting period:** January 12, 2023 – December 21, 2025.
- **Data type:** Aggregate operational counts.

These details describe the analyzed dataset version and should be revalidated if the source data changes.

### Data Limitations

- The data does not contain person-level identifiers linking events across stages.
- The data does not provide linked timestamps for individual transitions.
- Reported counts may represent different types of measures, including event flows and care workload.
- Missing, blank, or invalid records may affect the completeness of the analysis.
- Descriptive patterns do not establish the causes of observed changes.

## 🔒 Data Responsibility

Before redistributing the source dataset, verify its applicable license, terms of use, and public-sharing permissions.

The public source-code repository does not need to contain the original dataset if redistribution is not permitted. The dashboard and its documentation should be configured to work with an authorized data source.

Avoid publishing confidential, restricted, or personally identifiable information.

## 🔮 Future Improvements

Potential extensions include:

- Adding automated data-quality validation.
- Improving anomaly detection for unusual reporting patterns.
- Adding configurable thresholds for operational indicators.
- Supporting authorized dataset uploads.
- Adding more detailed data-quality reports.
- Improving dashboard accessibility and mobile responsiveness.
- Introducing automated refreshes when an authorized updated dataset becomes available.
- Expanding automated tests for data cleaning and metric calculations.

## 🎓 Learning Outcomes

This project demonstrates practical experience with:

- Python-based data analytics.
- Data cleaning and transformation.
- Exploratory data analysis.
- KPI and descriptive metric development.
- Interactive data visualization.
- Dashboard development using Streamlit.
- Git and GitHub version control.
- Cloud deployment.
- Communicating data limitations responsibly.

## 👩‍💻 Author

**Pranjali Tiwari**

Computer Science and Engineering

Interested in Data Analytics, Python Development, Data Visualization, and Software Engineering.

- **GitHub:** [Pranjali-0712](https://github.com/Pranjali-0712)
- **LinkedIn:** [Connect on LinkedIn](https://linkedin.com/in/pranjali-916776389)

## 📄 License

No license is specified for this project at present. Unless a license is added, others should not assume that the source code or accompanying materials are available for unrestricted reuse.

---

<p align="center">
  <strong>Turning aggregate reporting data into interactive analytical insights.</strong>
</p>
