import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from metrics import prepare_data, monthly_summary, kpis


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Care Transition Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("Care Transition Efficiency & Placement Outcome Analytics")

st.caption(
    "CBP custody → HHS care → sponsor discharge | "
    "Aggregate flow, workload and bottleneck analytics"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    file_path = ROOT / "data" / "HHS_Unaccompanied_Alien_Children_Program.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    raw_data = pd.read_csv(file_path)
    return prepare_data(raw_data)


try:
    df = load_data()
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


if df.empty:
    st.error("No valid reporting records were found in the dataset.")
    st.stop()


# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------

with st.sidebar:
    st.header("Dashboard Controls")

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    selected_dates = st.date_input(
        "Reporting date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(selected_dates, (tuple, list)):
        if len(selected_dates) == 2:
            start_date = pd.Timestamp(selected_dates[0])
            end_date = pd.Timestamp(selected_dates[1])

            f = df[
                (df["Date"] >= start_date)
                & (df["Date"] < end_date + pd.Timedelta(days=1))
            ].copy()

        elif len(selected_dates) == 1:
            selected_day = pd.Timestamp(selected_dates[0])

            f = df[
                df["Date"].dt.date == selected_day.date()
            ].copy()

        else:
            f = df.copy()

    else:
        selected_day = pd.Timestamp(selected_dates)

        f = df[
            df["Date"].dt.date == selected_day.date()
        ].copy()

    st.divider()

    ratio_mode = st.radio(
        "Metric display",
        ["Percentage / ratio", "Children / volume"],
        index=0,
    )

    threshold = st.slider(
        "Inflow–outflow imbalance alert (%)",
        min_value=-100,
        max_value=100,
        value=20,
        step=5,
        help=(
            "Flags reporting days where apprehensions exceed discharges "
            "by more than the selected percentage of apprehensions. "
            "This is an imbalance proxy, not a measured backlog."
        ),
    )

    st.divider()

    st.info(
        "The dataset contains aggregate reporting-day counts, "
        "not individual child records or transition timestamps. "
        "Therefore, the ratios are analytical proxies rather than "
        "actual waiting-time or case-level success measurements."
    )


if f.empty:
    st.warning(
        "No reporting records exist for the selected date range. "
        "Please select a different date range."
    )
    st.stop()


# --------------------------------------------------
# CALCULATE METRICS
# --------------------------------------------------

K = kpis(f)
monthly = monthly_summary(f)

if monthly.empty:
    st.warning("No monthly summary could be calculated.")
    st.stop()


# Create chart-friendly copies
monthly = monthly.copy()

monthly["Net Inflow vs Discharge"] = (
    monthly["Apprehended"] - monthly["Discharges"]
)

monthly["Cumulative Net Flow Proxy"] = (
    monthly["Net Inflow vs Discharge"].cumsum()
)


# --------------------------------------------------
# 1. EXECUTIVE KPI SUMMARY
# --------------------------------------------------

st.markdown("## 1. Executive KPI Summary")

c1, c2, c3, c4, c5 = st.columns(5)


def display_metric(value, suffix=""):
    if value is None or pd.isna(value) or not np.isfinite(value):
        return "N/A"

    return f"{value:,.1f}{suffix}"


c1.metric(
    "Transfer / CBP Stock Ratio",
    display_metric(K["avg_transfer_efficiency"], "%"),
)

c2.metric(
    "Discharge / HHS Stock Ratio",
    display_metric(K["avg_discharge_effectiveness"], "%"),
)

c3.metric(
    "Discharge-to-Intake Ratio",
    display_metric(K["pipeline_throughput"], "%"),
)

c4.metric(
    "Net Inflow–Outflow Imbalance",
    display_metric(K["net_inflow_outflow_imbalance"], "%"),
)

c5.metric(
    "Outcome Consistency Indicator",
    display_metric(K["outcome_stability_score"], "/100"),
)


st.caption(
    "These indicators summarize aggregate reporting data. "
    "They do not measure individual processing times or prove "
    "that each discharge corresponds to an intake recorded in the same period."
)


s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Reported apprehensions",
    f"{K['total_apprehended']:,.0f}",
)

s2.metric(
    "Reported transfers",
    f"{K['total_transfers']:,.0f}",
)

s3.metric(
    "Reported discharges",
    f"{K['total_discharges']:,.0f}",
)

s4.metric(
    "Average reported HHS care load",
    f"{K['avg_hhs_care']:,.0f}",
)


st.markdown("---")


# --------------------------------------------------
# 2. CARE PIPELINE VISUALIZATION
# --------------------------------------------------

st.markdown("## 2. Care Pipeline Flow Visualization")

st.write(
    "The chart below shows reported movement volumes and average "
    "reported care loads separately. These quantities represent "
    "different types of measures and should not be interpreted "
    "as a strict child-by-child funnel."
)

flow_left, flow_right = st.columns(2)

with flow_left:
    flow_data = pd.DataFrame(
        {
            "Stage": [
                "Apprehensions",
                "Transfers out of CBP",
                "Discharges from HHS",
            ],
            "Reported volume": [
                K["total_apprehended"],
                K["total_transfers"],
                K["total_discharges"],
            ],
        }
    )

    fig = px.bar(
        flow_data,
        x="Stage",
        y="Reported volume",
        color="Stage",
        title="Aggregate movement volumes",
        text_auto=".3s",
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Reported movement",
        yaxis_title="Children / reported events",
    )

    st.plotly_chart(fig, use_container_width=True)


with flow_right:
    stock_data = pd.DataFrame(
        {
            "Reported stock measure": [
                "Average CBP custody",
                "Average HHS care",
            ],
            "Average reported count": [
                K["avg_cbp_custody"],
                K["avg_hhs_care"],
            ],
        }
    )

    fig = px.bar(
        stock_data,
        x="Reported stock measure",
        y="Average reported count",
        color="Reported stock measure",
        title="Average reported care loads",
        text_auto=".3s",
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Reporting stock",
        yaxis_title="Average reported count",
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 3. TRANSFER AND DISCHARGE INDICATORS
# --------------------------------------------------

st.markdown("## 3. Transfer & Discharge Indicators")

left, right = st.columns(2)

with left:
    fig = px.line(
        monthly,
        x="Month",
        y="Transfer_Efficiency",
        markers=True,
        title="Monthly transfer-to-reported-CBP-stock ratio",
    )

    fig.update_yaxes(title="Ratio (%)")

    st.plotly_chart(fig, use_container_width=True)


with right:
    fig = px.line(
        monthly,
        x="Month",
        y="Discharge_Effectiveness",
        markers=True,
        title="Monthly discharge-to-reported-HHS-stock ratio",
    )

    fig.update_yaxes(title="Ratio (%)")

    st.plotly_chart(fig, use_container_width=True)


st.markdown("### Flow and ratio comparison")

if ratio_mode == "Percentage / ratio":

    ratio_columns = [
        "Transfer_Efficiency",
        "Discharge_Effectiveness",
        "Pipeline_Throughput",
    ]

    ratio_long = monthly.melt(
        id_vars=["Month"],
        value_vars=ratio_columns,
        var_name="Metric",
        value_name="Ratio (%)",
    )

    fig = px.line(
        ratio_long,
        x="Month",
        y="Ratio (%)",
        color="Metric",
        markers=True,
        title="Monthly flow and ratio indicators",
    )

    fig.update_yaxes(title="Ratio (%)")

else:

    volume_columns = [
        "Apprehended",
        "Transfers",
        "Discharges",
    ]

    volume_long = monthly.melt(
        id_vars=["Month"],
        value_vars=volume_columns,
        var_name="Reported movement",
        value_name="Reported count",
    )

    fig = px.line(
        volume_long,
        x="Month",
        y="Reported count",
        color="Reported movement",
        markers=True,
        title="Monthly movement volumes",
    )

    fig.update_yaxes(title="Children / reported events")


st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 4. BOTTLENECK AND IMBALANCE ANALYSIS
# --------------------------------------------------

st.markdown("## 4. Bottleneck & Inflow–Outflow Analysis")

st.caption(
    "Apprehensions minus discharges is used as a net flow proxy. "
    "It is not a direct measure of the number of children waiting "
    "in the system because the two events may relate to different cohorts."
)

b1, b2 = st.columns(2)

with b1:
    fig = px.bar(
        monthly,
        x="Month",
        y="Net Inflow vs Discharge",
        title="Monthly apprehensions minus discharges",
        color="Net Inflow vs Discharge",
        color_continuous_scale="RdYlGn_r",
    )

    fig.add_hline(y=0, line_dash="dash")

    fig.update_yaxes(title="Apprehensions − discharges")

    st.plotly_chart(fig, use_container_width=True)


with b2:
    fig = px.line(
        monthly,
        x="Month",
        y="Cumulative Net Flow Proxy",
        markers=True,
        title="Cumulative net flow proxy",
    )

    fig.add_hline(y=0, line_dash="dash")

    fig.update_yaxes(title="Cumulative proxy count")

    st.plotly_chart(fig, use_container_width=True)


fig = px.line(
    f,
    x="Date",
    y="Backlog_Accumulation_Rate",
    title="Daily net inflow–outflow imbalance proxy",
    markers=False,
)

fig.add_hline(
    y=threshold,
    line_dash="dash",
    annotation_text="Selected alert threshold",
)

fig.update_yaxes(title="Imbalance proxy (%)")

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 5. TEMPORAL AND WEEKDAY PATTERNS
# --------------------------------------------------

st.markdown("## 5. Temporal & Pattern Analysis")

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

weekday = (
    f.groupby("Weekday", as_index=False)
    .agg(
        Transfer_Efficiency=("Transfer_Efficiency", "mean"),
        Discharge_Effectiveness=("Discharge_Effectiveness", "mean"),
        Pipeline_Throughput=("Pipeline_Throughput", "mean"),
        Discharges=("Discharges", "mean"),
    )
)

weekday["Weekday"] = pd.Categorical(
    weekday["Weekday"],
    categories=weekday_order,
    ordered=True,
)

weekday = weekday.sort_values("Weekday")


t1, t2 = st.columns(2)

with t1:
    fig = px.bar(
        weekday,
        x="Weekday",
        y="Transfer_Efficiency",
        title="Average transfer-to-CBP-stock ratio by weekday",
    )

    fig.update_yaxes(title="Average daily ratio (%)")

    st.plotly_chart(fig, use_container_width=True)


with t2:
    fig = px.bar(
        weekday,
        x="Weekday",
        y="Discharge_Effectiveness",
        title="Average discharge-to-HHS-stock ratio by weekday",
    )

    fig.update_yaxes(title="Average daily ratio (%)")

    st.plotly_chart(fig, use_container_width=True)


weekend_summary = (
    f.groupby("Weekend", as_index=False)
    .agg(
        Reporting_Days=("Date", "count"),
        Avg_Transfer_Ratio=("Transfer_Efficiency", "mean"),
        Avg_Discharge_Ratio=("Discharge_Effectiveness", "mean"),
        Avg_Discharge_Count=("Discharges", "mean"),
        Total_Apprehended=("Apprehended", "sum"),
        Total_Transfers=("Transfers", "sum"),
        Total_Discharges=("Discharges", "sum"),
    )
)

st.markdown("### Weekday versus weekend comparison")

st.dataframe(
    weekend_summary,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# 6. OUTCOME TREND AND STABILITY
# --------------------------------------------------

st.markdown("## 6. Outcome Trend & Stability Analysis")

st.caption(
    "The stability indicator measures variation in the discharge ratio. "
    "It does not measure whether individual placements were successful."
)

stability = f[
    [
        "Date",
        "Discharge_Effectiveness",
        "Outcome_Stability_Score",
    ]
].copy()

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=stability["Date"],
        y=stability["Discharge_Effectiveness"],
        name="Discharge-to-HHS-stock ratio",
        mode="lines",
    )
)

fig.add_trace(
    go.Scatter(
        x=stability["Date"],
        y=stability["Outcome_Stability_Score"],
        name="Rolling consistency indicator",
        mode="lines",
    )
)

fig.update_layout(
    title="Discharge ratio and rolling consistency indicator",
    xaxis_title="Date",
    yaxis_title="Ratio (%) / score",
)

st.plotly_chart(fig, use_container_width=True)


fig = px.line(
    monthly,
    x="Month",
    y="Outcome_Stability_Score",
    markers=True,
    title="Monthly outcome consistency indicator",
)

fig.add_hline(
    y=80,
    line_dash="dash",
    annotation_text="Reference level: 80",
)

fig.update_yaxes(title="Consistency indicator (0–100)")

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 7. THRESHOLD-BASED ALERTS
# --------------------------------------------------

st.markdown("## 7. Threshold-Based Visual Alerts")

alerts = f[
    f["Backlog_Accumulation_Rate"].notna()
    & (f["Backlog_Accumulation_Rate"] > threshold)
].sort_values(
    "Backlog_Accumulation_Rate",
    ascending=False,
)

if alerts.empty:

    st.success(
        "No reporting days exceed the selected imbalance threshold."
    )

else:

    st.warning(
        f"{len(alerts)} reporting days exceed the selected "
        f"imbalance threshold of {threshold:.0f}%."
    )

    st.dataframe(
        alerts[
            [
                "Date",
                "Apprehended",
                "Transfers",
                "Discharges",
                "Backlog_Accumulation_Rate",
            ]
        ].head(25),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download all flagged reporting days",
        alerts.to_csv(index=False).encode("utf-8"),
        "care_transition_flagged_days.csv",
        "text/csv",
    )


# --------------------------------------------------
# 8. AUTOMATED FINDINGS
# --------------------------------------------------

st.markdown("## 8. Automated Findings")


def report_extreme(data, column, highest=True):
    valid = data.dropna(subset=[column])

    if valid.empty:
        return None

    index = valid[column].idxmax() if highest else valid[column].idxmin()

    return valid.loc[index]


best_transfer = report_extreme(
    monthly, "Transfer_Efficiency", highest=True
)

worst_transfer = report_extreme(
    monthly, "Transfer_Efficiency", highest=False
)

best_discharge = report_extreme(
    monthly, "Discharge_Effectiveness", highest=True
)

worst_discharge = report_extreme(
    monthly, "Discharge_Effectiveness", highest=False
)

peak_imbalance = report_extreme(
    monthly, "Net Inflow vs Discharge", highest=True
)


findings = []

if best_transfer is not None:
    findings.append(
        f"Highest monthly transfer-to-CBP-stock ratio: "
        f"{best_transfer['Month']} "
        f"({best_transfer['Transfer_Efficiency']:.1f}%)."
    )

if worst_transfer is not None:
    findings.append(
        f"Lowest monthly transfer-to-CBP-stock ratio: "
        f"{worst_transfer['Month']} "
        f"({worst_transfer['Transfer_Efficiency']:.1f}%)."
    )

if best_discharge is not None:
    findings.append(
        f"Highest monthly discharge-to-HHS-stock ratio: "
        f"{best_discharge['Month']} "
        f"({best_discharge['Discharge_Effectiveness']:.1f}%)."
    )

if worst_discharge is not None:
    findings.append(
        f"Lowest monthly discharge-to-HHS-stock ratio: "
        f"{worst_discharge['Month']} "
        f"({worst_discharge['Discharge_Effectiveness']:.1f}%)."
    )

if peak_imbalance is not None:
    findings.append(
        f"Largest monthly apprehension-minus-discharge difference: "
        f"{peak_imbalance['Month']} "
        f"({peak_imbalance['Net Inflow vs Discharge']:,.0f})."
    )

if findings:
    for item in findings:
        st.write(f"• {item}")
else:
    st.info("There are not enough valid monthly values to generate findings.")


# --------------------------------------------------
# 9. DATA QUALITY AND METHODOLOGY
# --------------------------------------------------

st.markdown("## 9. Data Quality, Methodology & Limitations")

st.write(f"Valid reporting records in the selected period: **{len(f):,}**")

st.write(
    f"Selected reporting period: **{f['Date'].min().date()}** "
    f"to **{f['Date'].max().date()}**"
)

st.info(
    "The source contains aggregate reporting-day counts, not "
    "individual child records or transition timestamps. Blank or "
    "invalid records are excluded during data preparation. "
    "Consequently, these analyses cannot establish exact waiting "
    "times, link a specific apprehension to a later transfer or "
    "discharge, or calculate individual placement success rates."
)

with st.expander("Metric definitions and interpretation"):

    st.markdown(
        """
**1. Transfer-to-CBP-stock ratio**

Reported transfers ÷ reported CBP custody count × 100.

This is a flow-to-reported-stock ratio. Because the denominator is a
reported stock count, it is not a conventional probability of transfer.

**2. Discharge-to-HHS-stock ratio**

Reported discharges ÷ reported HHS care count × 100.

This is a flow-to-reported-stock ratio, not a direct measure of
individual discharge success.

**3. Discharge-to-intake ratio**

Reported HHS discharges ÷ reported apprehensions × 100.

This ratio may exceed 100% because discharges in a period can relate
to children who entered care before that period.

**4. Net inflow–outflow imbalance proxy**

(Apprehensions − discharges) ÷ apprehensions × 100.

This compares two reported flows. It is not a measured change in the
number of children waiting in care.

**5. Outcome consistency indicator**

A coefficient-of-variation-based indicator derived from discharge ratios,
clipped to a range of 0–100. Higher values indicate lower relative
variation in the measured ratio over the relevant window.

This is not a measure of placement quality or successful reunification.

**6. Weekday and weekend comparison**

Compares reporting-day indicators and counts by weekday category.
The results show patterns in reported data, not actual processing times.

**7. Cumulative net flow proxy**

A cumulative sum of apprehensions minus discharges in the selected period.
It is a directional comparison of flows and must not be interpreted as
the true cumulative backlog.
        """
    )


# --------------------------------------------------
# DOWNLOADS
# --------------------------------------------------

st.markdown("## Download Results")

d1, d2 = st.columns(2)

with d1:
    st.download_button(
        "Download filtered reporting data",
        f.to_csv(index=False).encode("utf-8"),
        "care_transition_filtered.csv",
        "text/csv",
    )

with d2:
    st.download_button(
        "Download monthly summary",
        monthly.to_csv(index=False).encode("utf-8"),
        "care_transition_monthly_summary.csv",
        "text/csv",
    )


st.caption(
    "Project focus: aggregate process-efficiency analytics for the "
    "unaccompanied children care pipeline. Interpret all flow ratios "
    "in the context of the source data's limitations."
)