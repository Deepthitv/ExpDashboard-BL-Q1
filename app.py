import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Bank Leumi Quarter 1 Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA (ROBUST VERSION)
# -----------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(
            "cases.csv",
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        df = pd.read_csv(
            "cases.csv",
            encoding="latin1",
            engine="python"
        )

    df['Opened Date'] = pd.to_datetime(df['Opened Date'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')

    return df


df = load_data()

# SAFETY CHECK
if df.empty:
    st.error("⚠️ Dataframe is empty. Check cases.csv formatting.")
    st.stop()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Filters")

tech = st.sidebar.multiselect(
    "Technology",
    df['Technology'].dropna().unique(),
    default=df['Technology'].dropna().unique()
)

status = st.sidebar.multiselect(
    "Status",
    df['Status'].dropna().unique(),
    default=df['Status'].dropna().unique()
)

priority = st.sidebar.multiselect(
    "Priority",
    df['Priority - Current (Text)'].dropna().unique(),
    default=df['Priority - Current (Text)'].dropna().unique()
)

filtered = df[
    (df['Technology'].isin(tech)) &
    (df['Status'].isin(status)) &
    (df['Priority - Current (Text)'].isin(priority))
]

# -----------------------------
# KPI CALCULATIONS
# -----------------------------
total_cases = len(filtered)
open_cases = len(filtered[~filtered['Status'].str.contains("Closed", na=False)])

avg_days_open = filtered['Days Open'].mean() if not filtered.empty else 0
avg_irt = filtered['Initial Response Time Min'].mean() if not filtered.empty else 0
avg_resolution = filtered['Final Resolution Time (Days)'].mean() if not filtered.empty else 0
total_rma = filtered['RMA Count'].sum() if not filtered.empty else 0

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 Bank Leumi Quarter 1 Dashboard")

# -----------------------------
# KPI ROW
# -----------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total SRs", int(total_cases))
c2.metric("Open Cases", int(open_cases))
c3.metric("Avg Days Open", round(avg_days_open,1) if pd.notna(avg_days_open) else 0)
c4.metric("Avg IRT (min)", round(avg_irt,1) if pd.notna(avg_irt) else 0)
c5.metric("Avg Resolution Days", round(avg_resolution,1) if pd.notna(avg_resolution) else 0)
c6.metric("Total RMA", int(total_rma))

st.divider()

# -----------------------------
# STATUS DISTRIBUTION
# -----------------------------
col1, col2 = st.columns(2)

status_fig = px.pie(
    filtered,
    names='Status',
    title="Case Status Distribution"
)
col1.plotly_chart(status_fig, use_container_width=True)

tech_counts = filtered['Technology'].value_counts().reset_index()
tech_counts.columns = ['Technology', 'Count']

tech_fig = px.bar(
    tech_counts,
    x='Count',
    y='Technology',
    orientation='h',
    title="Cases by Technology"
)
col2.plotly_chart(tech_fig, use_container_width=True)

# -----------------------------
# TREND ANALYSIS (FIXED BUG)
# -----------------------------
st.subheader("📈 Case Trend Over Time")

trend = (
    filtered
    .groupby(filtered['Opened Date'].dt.date)
    .size()
    .reset_index(name='Cases')
)

trend.columns = ['Opened Date', 'Cases']

trend_fig = px.line(
    trend,
    x='Opened Date',
    y='Cases',
    title="Cases Opened Over Time"
)

st.plotly_chart(trend_fig, use_container_width=True)

# -----------------------------
# PERFORMANCE ANALYSIS
# -----------------------------
col3, col4 = st.columns(2)

irt_fig = px.box(
    filtered,
    y='Initial Response Time Min',
    title="Initial Response Time Distribution"
)
col3.plotly_chart(irt_fig, use_container_width=True)

days_open_fig = px.box(
    filtered,
    y='Days Open',
    title="Days Open Distribution"
)
col4.plotly_chart(days_open_fig, use_container_width=True)

# -----------------------------
# OWNER WORKLOAD
# -----------------------------
st.subheader("👩‍💻 Case Owner Load")

owner_load = filtered['Case Owner'].value_counts().reset_index()
owner_load.columns = ['Owner','Cases']

owner_fig = px.bar(
    owner_load,
    x='Owner',
    y='Cases',
    title="Cases per Owner"
)

st.plotly_chart(owner_fig, use_container_width=True)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📋 Case Details")

st.dataframe(filtered, use_container_width=True)
