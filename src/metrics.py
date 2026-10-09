import numpy as np
import pandas as pd


# ============================================================
# 1. RAW DATA COLUMN MAPPING
# ============================================================

RAW_TO_CLEAN = {
    "Date": "Date",
    "Children apprehended and placed in CBP custody*": "Apprehended",
    "Children in CBP custody": "CBP_Custody",
    "Children transferred out of CBP custody": "Transfers",
    "Children in HHS Care": "HHS_Care",
    "Children discharged from HHS Care": "Discharges",
}

NUMERIC_COLUMNS = [
    "Apprehended",
    "CBP_Custody",
    "Transfers",
    "HHS_Care",
    "Discharges",
]


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def safe_percentage(numerator, denominator):
    """
    Calculate a percentage safely.

    Returns NaN when the denominator is zero or missing.
    """
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(
            np.isfinite(denominator) & (denominator > 0),
            numerator / denominator * 100,
            np.nan,
        )

    return result


def calculate_stability_score(values):
    """
    Calculate a discharge-effectiveness stability score.

    Formula:
        Stability Score = 100 * (1 - coefficient of variation)

    The result is clipped to 0–100.

    A higher score indicates lower relative variability.
    This is a statistical stability indicator, not a measure
    of placement success or child welfare outcomes.
    """
    series = pd.Series(values, dtype="float64").replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    if len(series) < 2:
        return np.nan

    mean_value = series.mean()
    std_value = series.std(ddof=1)

    if not np.isfinite(mean_value) or abs(mean_value) < 1e-12:
        return np.nan

    coefficient_of_variation = std_value / abs(mean_value)

    score = 100 * (1 - coefficient_of_variation)

    return float(np.clip(score, 0, 100))


# ============================================================
# 3. DATA CLEANING AND PREPARATION
# ============================================================

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the source dataset and calculate daily indicators.

    Important:
    The dataset contains aggregate reporting-day counts,
    not individual case records or transition timestamps.
    Therefore, the calculated indicators are flow-based
    proxies, not actual transition-time measurements.
    """

    df = df.copy()

    # Standardize column names.
    df = df.rename(columns=RAW_TO_CLEAN)

    required_columns = list(RAW_TO_CLEAN.values())

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Parse dates.
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
    )

    # Convert numeric fields safely.
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(
            df[column]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.strip(),
            errors="coerce",
        )

    # Remove blank and invalid reporting rows.
    df = df.dropna(
        subset=["Date"] + NUMERIC_COLUMNS
    ).copy()

    # Sort records chronologically.
    df = df.sort_values("Date").reset_index(drop=True)

    # Avoid interpreting impossible negative counts as valid data.
    if (df[NUMERIC_COLUMNS] < 0).any().any():
        raise ValueError(
            "Negative values were found in the count columns. "
            "Inspect the source dataset before continuing."
        )

    # Add temporal fields.
    df["Weekday"] = df["Date"].dt.day_name()

    df["Weekend"] = np.where(
        df["Date"].dt.dayofweek >= 5,
        "Weekend",
        "Weekday",
    )

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    df["Year"] = df["Date"].dt.year

    # --------------------------------------------------------
    # DAILY FLOW INDICATORS
    # --------------------------------------------------------

    # Transfer Efficiency:
    # Transfers / CBP Custody * 100
    df["Transfer_Efficiency"] = safe_percentage(
        df["Transfers"],
        df["CBP_Custody"],
    )

    # Discharge Effectiveness:
    # Discharges / HHS Care * 100
    df["Discharge_Effectiveness"] = safe_percentage(
        df["Discharges"],
        df["HHS_Care"],
    )

    # Pipeline Throughput:
    # Discharges / Apprehensions * 100
    df["Pipeline_Throughput"] = safe_percentage(
        df["Discharges"],
        df["Apprehended"],
    )

    # --------------------------------------------------------
    # NET INFLOW–OUTFLOW IMBALANCE
    # --------------------------------------------------------

    # Positive: apprehensions exceeded discharges.
    # Negative: discharges exceeded apprehensions.
    #
    # This is NOT an actual count of unresolved cases.
    df["Backlog_Change"] = (
        df["Apprehended"] - df["Discharges"]
    )

    df["Backlog_Accumulation_Rate"] = safe_percentage(
        df["Backlog_Change"],
        df["Apprehended"],
    )

    # Retain a clear alias for use in newer dashboard code.
    df["Net_Inflow_Outflow_Imbalance"] = (
        df["Backlog_Accumulation_Rate"]
    )

    # --------------------------------------------------------
    # STAGE-LEVEL FLOW IMBALANCE PROXIES
    # --------------------------------------------------------

    # Positive: apprehensions exceeded transfers.
    df["Net_CBP_Flow"] = (
        df["Apprehended"] - df["Transfers"]
    )

    # Positive: transfers exceeded discharges.
    df["Net_HHS_Flow"] = (
        df["Transfers"] - df["Discharges"]
    )

    # Retained for compatibility with the existing dashboard.
    df["Backlog_Pressure"] = df["Backlog_Change"]

    # --------------------------------------------------------
    # OUTCOME STABILITY
    # --------------------------------------------------------

    # Use a rolling 30-reporting-record window.
    # At least 7 valid observations are required.
    rolling_mean = (
        df["Discharge_Effectiveness"]
        .rolling(window=30, min_periods=7)
        .mean()
    )

    rolling_std = (
        df["Discharge_Effectiveness"]
        .rolling(window=30, min_periods=7)
        .std(ddof=1)
    )

    coefficient_of_variation = (
        rolling_std / rolling_mean.abs().replace(0, np.nan)
    )

    df["Outcome_Stability_Score"] = (
        100 * (1 - coefficient_of_variation)
    ).clip(lower=0, upper=100)

    return df


# ============================================================
# 4. MONTHLY SUMMARY
# ============================================================

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create monthly totals, averages, flow ratios and
    stability indicators.

    Monthly efficiency ratios are calculated using the
    ratio of monthly totals, rather than the average of
    daily percentages.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Month",
                "Apprehended",
                "Transfers",
                "Discharges",
                "Avg_CBP_Custody",
                "Avg_HHS_Care",
                "Transfer_Efficiency",
                "Discharge_Effectiveness",
                "Pipeline_Throughput",
                "Backlog_Change",
                "Backlog_Accumulation_Rate",
                "Net_Inflow_Outflow_Imbalance",
                "Outcome_Stability_Score",
            ]
        )

    out = (
        df.groupby("Month", as_index=False)
        .agg(
            Apprehended=("Apprehended", "sum"),
            Transfers=("Transfers", "sum"),
            Discharges=("Discharges", "sum"),
            Avg_CBP_Custody=("CBP_Custody", "mean"),
            Avg_HHS_Care=("HHS_Care", "mean"),
        )
    )

    # Monthly CBP and HHS totals are denominators for the
    # monthly flow indicators.
    monthly_cbp = (
        df.groupby("Month")["CBP_Custody"].sum()
    )

    monthly_hhs = (
        df.groupby("Month")["HHS_Care"].sum()
    )

    out["Transfer_Efficiency"] = safe_percentage(
        out["Transfers"],
        out["Month"].map(monthly_cbp),
    )

    out["Discharge_Effectiveness"] = safe_percentage(
        out["Discharges"],
        out["Month"].map(monthly_hhs),
    )

    out["Pipeline_Throughput"] = safe_percentage(
        out["Discharges"],
        out["Apprehended"],
    )

    # Monthly net inflow–outflow imbalance.
    out["Backlog_Change"] = (
        out["Apprehended"] - out["Discharges"]
    )

    out["Backlog_Accumulation_Rate"] = safe_percentage(
        out["Backlog_Change"],
        out["Apprehended"],
    )

    out["Net_Inflow_Outflow_Imbalance"] = (
        out["Backlog_Accumulation_Rate"]
    )

    # Three-month rolling stability score.
    out["Outcome_Stability_Score"] = (
        out["Discharge_Effectiveness"]
        .rolling(window=3, min_periods=2)
        .apply(
            calculate_stability_score,
            raw=False,
        )
    )

    return out


# ============================================================
# 5. OVERALL KPI SUMMARY
# ============================================================

def kpis(df: pd.DataFrame) -> dict:
    """
    Calculate overall dashboard KPIs.

    Overall transfer and discharge ratios use the ratio
    of totals. Daily average ratios are also returned
    separately for optional reporting.
    """

    if df.empty:
        return {
            "records": 0,
            "avg_transfer_efficiency": np.nan,
            "avg_discharge_effectiveness": np.nan,
            "daily_avg_transfer_efficiency": np.nan,
            "daily_avg_discharge_effectiveness": np.nan,
            "pipeline_throughput": np.nan,
            "backlog_accumulation_rate": np.nan,
            "net_inflow_outflow_imbalance": np.nan,
            "outcome_stability_score": np.nan,
            "total_apprehended": 0,
            "total_transfers": 0,
            "total_discharges": 0,
            "avg_hhs_care": np.nan,
            "avg_cbp_custody": np.nan,
            "transfer_flow_ratio": np.nan,
            "discharge_flow_ratio": np.nan,
        }

    total_apprehended = float(df["Apprehended"].sum())

    total_transfers = float(df["Transfers"].sum())

    total_discharges = float(df["Discharges"].sum())

    total_cbp = float(df["CBP_Custody"].sum())

    total_hhs = float(df["HHS_Care"].sum())

    # Overall ratios calculated consistently from totals.
    transfer_flow_ratio = (
        total_transfers / total_cbp * 100
        if total_cbp > 0
        else np.nan
    )

    discharge_flow_ratio = (
        total_discharges / total_hhs * 100
        if total_hhs > 0
        else np.nan
    )

    pipeline_throughput = (
        total_discharges / total_apprehended * 100
        if total_apprehended > 0
        else np.nan
    )

    net_imbalance = (
        (total_apprehended - total_discharges)
        / total_apprehended
        * 100
        if total_apprehended > 0
        else np.nan
    )

    # Keep the existing dashboard key names, but make the
    # primary overall KPIs consistent with ratios of totals.
    avg_transfer_efficiency = transfer_flow_ratio

    avg_discharge_effectiveness = discharge_flow_ratio

    # Daily mean ratios are retained separately for users
    # who want an unweighted average across reporting days.
    daily_avg_transfer_efficiency = (
        df["Transfer_Efficiency"].mean()
    )

    daily_avg_discharge_effectiveness = (
        df["Discharge_Effectiveness"].mean()
    )

    stability_score = calculate_stability_score(
        df["Discharge_Effectiveness"]
    )

    return {
        "records": int(len(df)),

        # Main overall KPI values.
        "avg_transfer_efficiency": avg_transfer_efficiency,
        "avg_discharge_effectiveness": avg_discharge_effectiveness,

        # Optional daily averages.
        "daily_avg_transfer_efficiency": (
            daily_avg_transfer_efficiency
        ),
        "daily_avg_discharge_effectiveness": (
            daily_avg_discharge_effectiveness
        ),

        "pipeline_throughput": pipeline_throughput,

        # Compatibility with the existing dashboard.
        "backlog_accumulation_rate": net_imbalance,

        # More precise label for this proxy.
        "net_inflow_outflow_imbalance": net_imbalance,

        "outcome_stability_score": stability_score,

        # Totals.
        "total_apprehended": int(total_apprehended),
        "total_transfers": int(total_transfers),
        "total_discharges": int(total_discharges),

        # Average reported custody counts.
        "avg_hhs_care": float(df["HHS_Care"].mean()),
        "avg_cbp_custody": float(df["CBP_Custody"].mean()),

        # Explicit flow ratios.
        "transfer_flow_ratio": transfer_flow_ratio,
        "discharge_flow_ratio": discharge_flow_ratio,
    }