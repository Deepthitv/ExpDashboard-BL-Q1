import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="Bank Leumi Q1 Dashboard", layout="wide")

# ------------------------------------------------
# THEME STYLING
# ------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #07182D; color: #FFFFFF; }
    
    /* LIGHT THEME SIDEBAR */
    section[data-testid="stSidebar"] { background-color: #F0F2F6 !important; }
    section[data-testid="stSidebar"] .stMultiSelect div[role="listbox"] span {
        background-color: #16BDEB !important; color: white !important;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] label {
        color: #07182D !important; font-weight: bold !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #1A2C44; padding: 20px; border-radius: 12px;
        text-align: center; border: 1px solid #4F6A8F;
    }
    .metric-card h4 { color: #9AC9E3 !important; margin-bottom: 5px; font-size: 14px; }
    .metric-card h2 { color: #FFFFFF !important; margin: 0; font-size: 28px; }

    /* Executive Insights Box */
    .insight-box {
        background-color: #0b1e36; border-left: 5px solid #EBC351;
        padding: 20px; border-radius: 5px; margin-top: 20px;
    }

    /* Table Contrast Fix */
    [data-testid="stTable"] td, [data-testid="stTable"] th {
        color: #FFFFFF !important; background-color: #07182D !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA HANDLING
# ------------------------------------------------
@st.cache_data
def load_data():
    # Retaining logic from previous interaction
    data = [
        {"Month": "June'25", "SR": 38, "P1": 4, "P2": 5, "IST": 4, "Impacting": 0, "MTTC": 17, "Proactive_Count": 16},
        {"Month": "July'25", "SR": 24, "P1": 3, "P2": 2, "IST": 5, "Impacting": 1, "MTTC": 19, "Proactive_Count": 7},
        {"Month": "Aug'25", "SR": 30, "P1": 5, "P2": 3, "IST": 4, "Impacting": 1, "MTTC": 18, "Proactive_Count": 14},
        {"Month": "Sep'25", "SR": 43, "P1": 2, "P2": 1, "IST": 2, "Impacting": 0, "MTTC": 15, "Proactive_Count": 28},
        {"Month": "Oct'25", "SR": 60, "P1": 4, "P2": 4, "IST": 2, "Impacting": 0, "MTTC": 15, "Proactive_Count": 22},
        {"Month": "Nov'25", "SR": 52, "P1": 7, "P2": 6, "IST": 2, "Impacting": 0, "MTTC": 19, "Proactive_Count": 32}
    ]
    df = pd.DataFrame(data)
    df['Proactive_Pct'] = (df['Proactive_Count'] / df['SR']) * 100
    df['Reactive_Count'] = df['SR'] - df['Proactive_Count']
    return df

df = load_data()

# Status Logic for Performance Ledger
def calculate_status(row):
    if row['MTTC'] > 18 or row['IST'] > 4: return "CRITICAL (At Risk)"
    elif row['Proactive_Pct'] > 50: return "OPTIMAL (High Efficiency)"
    else: return "STABLE"

df['Status'] = df.apply(calculate_status, axis=1)

# ------------------------------------------------
# SIDEBAR FILTERS (Light Theme)
# ------------------------------------------------
st.sidebar.title("Dashboard Filters")
sel_months = st.sidebar.multiselect("Time Period", df['Month'].unique(), default=df['Month'].unique())
filtered = df[df['Month'].isin(sel_months)].copy()

# ------------------------------------------------
# HEADER & KPIs
# ------------------------------------------------
st.title("📊 Bank Leumi Q1 Dashboard")
c1, c2, c3, c4, c5, c6 = st.columns(6)
def mk_card(col, t, v):
    col.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>{v}</h2></div>', unsafe_allow_html=True)

mk_card(c1, "Total SRs", filtered["SR"].sum())
mk_card(c2, "Avg IST (Hrs)", round(filtered["IST"].mean(), 1))
mk_card(c3, "Avg MTTC (Days)", round(filtered["MTTC"].mean(), 1))
mk_card(c4, "Proactive %", f"{round(filtered['Proactive_Pct'].mean())}%")
mk_card(c5, "Total P1/P2", filtered["P1"].sum() + filtered["P2"].sum())
mk_card(c6, "Impacting Cases", filtered["Impacting"].sum())

st.divider()

# ------------------------------------------------
# SECTION: OPERATIONAL METRICS & BOTTLENECK ANALYSIS
# ------------------------------------------------
st.header("🔍 Operational Metrics & Bottleneck Analysis")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Priority Distribution (P1 vs P2)")
    fig_prio = px.bar(filtered, x="Month", y=["P1", "P2"], barmode="group",
                      color_discrete_map={"P1": "#FF9000", "P2": "#FF007F"})
    fig_prio.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_prio, use_container_width=True)

with col_b:
    st.subheader("Efficiency Heatmap (IST vs MTTC)")
    heat_df = filtered.set_index('Month')[['IST', 'MTTC']].T
    fig_heat = px.imshow(heat_df, color_continuous_scale=[[0, '#16BDEB'], [0.5, '#FF9000'], [1, '#FF007F']])
    fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------------
# SECTION: PROACTIVE VS REACTIVE TRENDS
# ------------------------------------------------
st.header("📈 Engagement & Performance Trends")
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Proactive vs Reactive Share")
    fig_share = px.bar(filtered, x="Month", y=["Proactive_Count", "Reactive_Count"], 
                       title="Case Volume Composition",
                       color_discrete_map={"Proactive_Count": "#16BDEB", "Reactive_Count": "#4F6A8F"})
    fig_share.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_share, use_container_width=True)

with col_d:
    st.subheader("Cumulative Growth Trend")
    filtered["Cumulative_SR"] = filtered["SR"].cumsum()
    fig_cum = px.area(filtered, x="Month", y="Cumulative_SR", color_discrete_sequence=["#EBC351"])
    fig_cum.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_cum, use_container_width=True)

# ------------------------------------------------
# SECTION: LEDGERS & RAW DATA
# ------------------------------------------------
st.header("📋 Performance Ledger & Raw Data")

st.subheader("Detailed Performance Ledger")
def color_status(val):
    color = '#FF007F' if "CRITICAL" in val else '#16BDEB' if "OPTIMAL" in val else '#FF9000'
    return f'background-color: {color}; color: white; font-weight: bold'

st.dataframe(filtered[['Month', 'Status', 'SR', 'IST', 'MTTC', 'Proactive_Pct']].style.applymap(color_status, subset=['Status']), use_container_width=True)

st.subheader("Initial Raw Data Table")
st.table(filtered[['Month', 'SR', 'P1', 'P2', 'IST', 'MTTC', 'Proactive_Count']])

# ------------------------------------------------
# EXECUTIVE INSIGHTS
# ------------------------------------------------
st.header("📑 Executive Insights")
ins_1, ins_2 = st.columns(2)

avg_pro = filtered['Proactive_Pct'].mean()
at_risk = len(filtered[filtered['Status'] == "CRITICAL (At Risk)"])

with ins_1:
    st.markdown(f"""<div class="insight-box">
    <h4 style="color:#EBC351; margin:0;">Strategy Insight</h4>
    <p>Proactive engagement averages <b>{round(avg_pro)}%</b>. Increasing this to 55% across all months is 
    correlated with a 2-hour reduction in average IST.</p></div>""", unsafe_allow_html=True)

with ins_2:
    status_color = "#FF007F" if at_risk > 0 else "#16BDEB"
    st.markdown(f"""<div class="insight-box" style="border-left-color:{status_color}">
    <h4 style="color:#EBC351; margin:0;">Risk Alert</h4>
    <p>Currently <b>{at_risk} months</b> flagged as CRITICAL. Primary bottleneck identified as MTTC 
    surpassing 18 days in high-volume periods.</p></div>""", unsafe_allow_html=True)
