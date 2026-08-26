from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Delivery Performance & Logistics Efficiency",
    page_icon="🚚",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent

csv_files = list(BASE_DIR.glob("*.csv")) + list((BASE_DIR / "data").glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("No CSV dataset found in the project.")

DATA_PATH = csv_files[0]

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="latin1")
    df["Delivery Gap (Days)"] = (
        df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
    )
    df["On Time Flag"] = (df["Late_delivery_risk"] == 0).astype(int)
    return df


def percent(value: float) -> str:
    return f"{value:.2f}%"


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    shipping_modes = sorted(df["Shipping Mode"].dropna().unique().tolist())
    selected_modes = st.sidebar.multiselect(
        "Shipping Mode", shipping_modes, default=shipping_modes
    )

    markets = sorted(df["Market"].dropna().unique().tolist())
    selected_markets = st.sidebar.multiselect(
        "Market", markets, default=markets
    )

    regions = sorted(df["Order Region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "Order Region", regions, default=regions
    )

    segments = sorted(df["Customer Segment"].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "Customer Segment", segments, default=segments
    )

    filtered = df[
        df["Shipping Mode"].isin(selected_modes)
        & df["Market"].isin(selected_markets)
        & df["Order Region"].isin(selected_regions)
        & df["Customer Segment"].isin(selected_segments)
    ].copy()

    # The supplied project dataset contains no order/shipping date field.
    # If a compatible date column is added later, this section automatically
    # enables the required date-range selector.
    date_candidates = [
        c for c in df.columns
        if "date" in c.lower() or "dateorders" in c.lower()
    ]
    if date_candidates:
        date_col = date_candidates[0]
        parsed = pd.to_datetime(df[date_col], errors="coerce")
        if parsed.notna().any():
            min_date = parsed.min().date()
            max_date = parsed.max().date()
            selected_dates = st.sidebar.date_input(
                "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
            )
            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
                filtered_dates = pd.to_datetime(filtered[date_col], errors="coerce")
                filtered = filtered[
                    filtered_dates.between(pd.Timestamp(start_date), pd.Timestamp(end_date))
                ]
    else:
        st.sidebar.caption(
            "Date filter unavailable because the supplied CSV has no date column."
        )

    return filtered


df = load_data(DATA_PATH)
filtered = apply_filters(df)

st.title("🚚 Delivery Performance, Delay Risk & Logistics Efficiency Analysis")
st.caption("Global supply-chain delivery diagnostics using the APL Logistics dataset")

if filtered.empty:
    st.warning("No records match the selected filters. Please broaden your selections.")
    st.stop()

# KPI calculations
on_time_rate = filtered["On Time Flag"].mean() * 100
late_risk_ratio = filtered["Late_delivery_risk"].mean() * 100
avg_delivery_gap = filtered["Delivery Gap (Days)"].mean()
positive_delay = filtered.loc[filtered["Delivery Gap (Days)"] > 0, "Delivery Gap (Days)"]
avg_late_delay = positive_delay.mean() if not positive_delay.empty else 0.0
shipping_efficiency = on_time_rate
regional_delay_index = avg_delivery_gap

st.subheader("Key Performance Indicators")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("On-Time Delivery Rate", percent(on_time_rate))
c2.metric("Avg Delivery Gap", f"{avg_delivery_gap:.2f} days")
c3.metric("Late Delivery Risk", percent(late_risk_ratio))
c4.metric("Shipping Efficiency Index", f"{shipping_efficiency:.2f}")
c5.metric("Regional Delay Index", f"{regional_delay_index:.2f}")

st.info(
    "Metric definitions: On-time/SLA compliance = 100 × (1 − mean Late_delivery_risk). "
    "Delivery Gap = actual shipping days − scheduled shipping days. "
    "Shipping Efficiency Index uses the SLA compliance percentage for the current selection. "
    "Regional Delay Index is the mean delivery gap in days for the current selection."
)

# Overview
st.subheader("1. Delivery Performance Overview")
left, right = st.columns(2)
with left:
    status_counts = filtered["Delivery Status"].value_counts().reset_index()
    status_counts.columns = ["Delivery Status", "Orders"]
    fig = px.bar(
        status_counts,
        x="Delivery Status",
        y="Orders",
        title="Delivery Status Distribution",
        text_auto=True,
    )
    st.plotly_chart(fig, use_container_width=True)
with right:
    perf = pd.DataFrame(
        {
            "Metric": ["On-time / no late risk", "Late delivery risk"],
            "Percent": [on_time_rate, late_risk_ratio],
        }
    )
    fig = px.pie(perf, names="Metric", values="Percent", title="On-Time vs Late Delivery Risk")
    st.plotly_chart(fig, use_container_width=True)

st.metric("Average Delay Among Late Orders", f"{avg_late_delay:.2f} days")

# Delay risk dashboard
st.subheader("2. Delay Risk Analysis Dashboard")
left, right = st.columns(2)
with left:
    risk_counts = filtered["Late_delivery_risk"].map({0: "No late risk", 1: "Late risk"}).value_counts().reset_index()
    risk_counts.columns = ["Risk Category", "Orders"]
    fig = px.bar(risk_counts, x="Risk Category", y="Orders", title="Late Delivery Risk Distribution", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.histogram(
        filtered,
        x="Delivery Gap (Days)",
        nbins=10,
        title="Delivery Gap Histogram",
        labels={"Delivery Gap (Days)": "Actual - Scheduled Shipping Days"},
    )
    st.plotly_chart(fig, use_container_width=True)

# Shipping mode comparison
st.subheader("3. Shipping Mode Comparison")
ship = (
    filtered.groupby("Shipping Mode")
    .agg(
        Orders=("Late_delivery_risk", "size"),
        Late_Risk_Ratio=("Late_delivery_risk", "mean"),
        Avg_Delivery_Gap=("Delivery Gap (Days)", "mean"),
        SLA_Compliance=("On Time Flag", "mean"),
    )
    .reset_index()
)
ship["Late_Risk_Ratio"] *= 100
ship["SLA_Compliance"] *= 100
ship["Efficiency_Index"] = ship["SLA_Compliance"]

left, right = st.columns(2)
with left:
    fig = px.bar(
        ship.sort_values("SLA_Compliance", ascending=False),
        x="Shipping Mode",
        y="SLA_Compliance",
        title="SLA Compliance by Shipping Mode",
        text_auto=".2f",
        labels={"SLA_Compliance": "SLA Compliance (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(
        ship.sort_values("Avg_Delivery_Gap"),
        x="Shipping Mode",
        y="Avg_Delivery_Gap",
        title="Average Delivery Gap by Shipping Mode",
        text_auto=".2f",
        labels={"Avg_Delivery_Gap": "Average Delivery Gap (Days)"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(ship.round(2), use_container_width=True, hide_index=True)

# Regional & market diagnostics
st.subheader("4. Regional & Market Diagnostics")
regional = (
    filtered.groupby(["Market", "Order Region"])
    .agg(
        Orders=("Late_delivery_risk", "size"),
        Late_Risk_Ratio=("Late_delivery_risk", "mean"),
        Avg_Delivery_Gap=("Delivery Gap (Days)", "mean"),
    )
    .reset_index()
)
regional["Late_Risk_Ratio"] *= 100

left, right = st.columns(2)
with left:
    region_rank = (
        filtered.groupby("Order Region")
        .agg(
            Orders=("Late_delivery_risk", "size"),
            Late_Risk_Ratio=("Late_delivery_risk", "mean"),
        )
        .reset_index()
    )
    region_rank["Late_Risk_Ratio"] *= 100
    fig = px.bar(
        region_rank.sort_values("Late_Risk_Ratio", ascending=False),
        x="Order Region",
        y="Late_Risk_Ratio",
        title="Late Delivery Risk by Order Region",
        labels={"Late_Risk_Ratio": "Late Delivery Risk (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)
with right:
    pivot = regional.pivot_table(index="Market", columns="Order Region", values="Late_Risk_Ratio")
    heatmap_df = pivot.reset_index().melt(id_vars="Market", var_name="Order Region", value_name="Late Risk %")
    heatmap_df = heatmap_df.dropna()
    fig = px.density_heatmap(
        heatmap_df,
        x="Order Region",
        y="Market",
        z="Late Risk %",
        histfunc="avg",
        title="Market × Region Late-Risk Heatmap",
    )
    st.plotly_chart(fig, use_container_width=True)

country = (
    filtered.groupby("Order Country")
    .agg(
        Orders=("Late_delivery_risk", "size"),
        Late_Risk_Ratio=("Late_delivery_risk", "mean"),
    )
    .reset_index()
)
country["Late_Risk_Ratio"] *= 100
fig = px.choropleth(
    country,
    locations="Order Country",
    locationmode="country names",
    color="Late_Risk_Ratio",
    hover_name="Order Country",
    hover_data={"Orders": True, "Late_Risk_Ratio": ":.2f"},
    title="Geographic Late-Delivery Risk by Order Country",
    labels={"Late_Risk_Ratio": "Late Risk (%)"},
)
st.plotly_chart(fig, use_container_width=True)

# Customer segment analysis
st.subheader("5. Customer Segment Impact Analysis")
segment = (
    filtered.groupby("Customer Segment")
    .agg(
        Orders=("Late_delivery_risk", "size"),
        Late_Risk_Ratio=("Late_delivery_risk", "mean"),
        Avg_Delivery_Gap=("Delivery Gap (Days)", "mean"),
    )
    .reset_index()
)
segment["Late_Risk_Ratio"] *= 100
left, right = st.columns(2)
with left:
    fig = px.bar(
        segment,
        x="Customer Segment",
        y="Late_Risk_Ratio",
        title="Late Delivery Risk by Customer Segment",
        text_auto=".2f",
        labels={"Late_Risk_Ratio": "Late Delivery Risk (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)
with right:
    fig = px.bar(
        segment,
        x="Customer Segment",
        y="Avg_Delivery_Gap",
        title="Average Delivery Gap by Customer Segment",
        text_auto=".2f",
        labels={"Avg_Delivery_Gap": "Average Delivery Gap (Days)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# Actionable insights
st.subheader("6. Operational Insights & Recommendations")
worst_mode = ship.sort_values("Late_Risk_Ratio", ascending=False).iloc[0]
best_mode = ship.sort_values("SLA_Compliance", ascending=False).iloc[0]
worst_region = region_rank.sort_values("Late_Risk_Ratio", ascending=False).iloc[0]
worst_segment = segment.sort_values("Late_Risk_Ratio", ascending=False).iloc[0]

st.markdown(
    f"""
- **Highest shipping-mode risk:** {worst_mode['Shipping Mode']} has a late-risk ratio of **{worst_mode['Late_Risk_Ratio']:.2f}%**.
- **Best shipping-mode SLA compliance:** {best_mode['Shipping Mode']} achieves **{best_mode['SLA_Compliance']:.2f}%** compliance.
- **Highest regional risk:** {worst_region['Order Region']} records **{worst_region['Late_Risk_Ratio']:.2f}%** late-delivery risk in the current selection.
- **Most exposed customer segment:** {worst_segment['Customer Segment']} has **{worst_segment['Late_Risk_Ratio']:.2f}%** late-delivery risk.
- Prioritize root-cause analysis for high-risk modes and regions, strengthen SLA monitoring, and consider routing high-priority orders through consistently higher-compliance shipping modes where operationally feasible.
"""
)

st.caption(
    "Data limitation: the provided APL_Logistics.csv has no order/shipping date field, so date-range filtering cannot be applied without a dated source file."
)
