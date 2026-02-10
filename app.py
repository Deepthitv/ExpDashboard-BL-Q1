import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Bank Leumi Quarter_1 Dashboard",
    layout="wide"
)

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():

    # Try multiple encodings to avoid UnicodeDecodeError
    try:
        df = pd.read_csv("cases.csv", encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv("cases.csv", encoding="latin1")
        except:
            df = pd.read_csv("cases.csv", encoding="cp1252", errors="replace")

    # Date parsing
    df['Opened Date'] = pd.to_datetime(df['Opened Date'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')

    return df


df = load_data()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.title("Filters")

tech = st.sidebar.multiselect(
    "Technology",
    sorted(df['Technology'].dropna().unique()),
    default=sorted(df['Technology'].dropna().unique())
)

status = st.sidebar.multiselect(
    "Status",
    sorted(df['Status'].dropna().unique()),
    default=sorted(df['Status'].dropna().unique())
)

priority = st.sidebar.multiselect(
    "Priority",
    sorted(df['Priority - Current (Text)'].dropna().unique()),
    default=sorted(df['Priority - Current (Text)'].dropna().unique())
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

avg_days_open = filtered['Days Open'].mean()
avg_irt = filtered['Initial Response Time Min'].mean()
avg_resolution = filtered['Final Resolution Time (Days)'].mean()
total_rma = filtered['RMA Count'].sum()

# -----------------------------
# HEADER
# -----------------------------
st.title("📊 HTOM Expert Care Operations Dashboard")

# -----------------------------
# KPI ROW
# -----------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total SRs", int(total_cases))
c2.metric("Open Cases", int(open_cases))
c3.metric("Avg Days Open", round(avg_days_open,1) if pd.notnull(avg_days_open) else 0)
c4.metric("Avg IRT (min)", round(avg_irt,1) if pd.notnull(avg_irt) else 0)
c5.metric("Avg Resolution Days", round(avg_resolution,1) if pd.notnull(avg_resolution) else 0)
c6.metric("Total RMA", int(total_rma) if pd.notnull(total_rma) else 0)

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

tech_counts = filtered['Technology'].value_counts().reset_index(name='count')
tech_counts.columns = ['Technology', 'count']

tech_fig = px.bar(
    tech_counts,
    x='count',
    y='Technology',
    orientation='h',
    title="Cases by Technology"
)

col2.plotly_chart(tech_fig, use_container_width=True)

# -----------------------------
# TREND ANALYSIS
# -----------------------------
st.subheader("📈 Case Trend Over Time")

trend = filtered.groupby(
    filtered['Opened Date'].dt.date
).size().reset_i_
