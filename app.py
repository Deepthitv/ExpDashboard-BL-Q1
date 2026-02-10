import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="HTOM Case Operations Dashboard",
    layout="wide"
)

# ------------------------------------------------
# THEME STYLING
# ------------------------------------------------
st.markdown("""
<style>

body {
    background-color: #07182D;
    color: #FFFFFF;
}

.main {
    background-color: #07182D;
}

h1, h2, h3 {
    color: #EBC351;
}

.metric-card {
    background-color: #1A2C44;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cases.csv", encoding="utf-8")
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

if df.empty:
    st.error("⚠️ Dataframe is empty. Check cases.csv formatting.")
    st.stop()

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------
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

# ------------------------------------------------
# KPI CALCULATIONS
# ------------------------------------------------
total_cases = len(filtered)
open_cases = len(filtered[~filtered['Status'].str.contains("Closed", na=False)])
avg_days_open = filtered['Days Open'].mean()
avg_irt = filtered['Initial Response Time Min'].mean()
avg_resolution = filtered['Final Resolution Time (Days)'].mean()
total_rma = filtered['RMA Count'].sum()

# ------------------------------------------------
# HEADER
# ------------------------------------------------
st.title("📊 HTOM Expert Care Operations Dashboard")

# ------------------------------------------------
# KPI CARDS
# ------------------------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

def metric_card(col, title, value):
    col.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

metric_card(c1,"Total SRs",total_cases)
metric_card(c2,"Open Cases",open_cases)
metric_card(c3,"Avg Days Open",round(avg_days_open,1))
metric_card(c4,"Avg IRT (min)",round(avg_irt,1))
metric_card(c5,"Avg Resolution Days",round(avg_resolution,1))
metric_card(c6,"Total RMA",int(total_rma))

st.divider()

# ------------------------------------------------
# STATUS + TECHNOLOGY
# ------------------------------------------------
col1, col2 = st.columns(2)

status_fig = px.pie(
    filtered,
    names='Status',
    color_discrete_sequence=["#4F6A8F","#9AC9E3"]
)
status_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)
col1.plotly_chart(status_fig, use_container_width=True)

tech_counts = filtered['Technology'].value_counts().reset_index()
tech_counts.columns = ['Technology','Count']

tech_fig = px.bar(
    tech_counts,
    x='Count',
    y='Technology',
    orientation='h',
    color_discrete_sequence=["#4F6A8F"]
)
tech_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)
col2.plotly_chart(tech_fig, use_container_width=True)

# ------------------------------------------------
# TREND ANALYSIS
# ------------------------------------------------
st.subheader("📈 Case Trend Over Time")

trend = (
    filtered
    .groupby(filtered['Opened Date'].dt.date)
    .size()
    .reset_index(name='Cases')
)

trend.columns = ['Opened Date','Cases']

trend_fig = px.line(
    trend,
    x='Opened Date',
    y='Cases'
)
trend_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)

st.plotly_chart(trend_fig, use_container_width=True)

# ------------------------------------------------
# PERFORMANCE ANALYSIS
# ------------------------------------------------
col3, col4 = st.columns(2)

irt_fig = px.box(
    filtered,
    y='Initial Response Time Min',
    color_discrete_sequence=["#9AC9E3"]
)
irt_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)

days_open_fig = px.box(
    filtered,
    y='Days Open',
    color_discrete_sequence=["#4F6A8F"]
)
days_open_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)

col3.plotly_chart(irt_fig, use_container_width=True)
col4.plotly_chart(days_open_fig, use_container_width=True)

# ------------------------------------------------
# CASE AGING RISK (REPLACEMENT FOR OWNER LOAD)
# ------------------------------------------------
st.subheader("🔥 Case Aging Risk Distribution")

bins = [0,7,30,90,9999]
labels = ['0-7 Days','8-30 Days','31-90 Days','90+ Days']

filtered['Age Bucket'] = pd.cut(
    filtered['Days Open'],
    bins=bins,
    labels=labels
)

aging = filtered['Age Bucket'].value_counts().reset_index()
aging.columns = ['Age Bucket','Cases']

aging_fig = px.bar(
    aging,
    x='Age Bucket',
    y='Cases',
    color_discrete_sequence=["#EBC351"]
)
aging_fig.update_layout(
    paper_bgcolor="#07182D",
    plot_bgcolor="#07182D",
    font_color="#FFFFFF"
)

st.plotly_chart(aging_fig, use_container_width=True)

# ------------------------------------------------
# DATA TABLE
# ------------------------------------------------
st.subheader("📋 Case Details")

st.dataframe(filtered, use_container_width=True)
