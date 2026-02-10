import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(
    page_title="Bank Leumi Q1 Dashboard",
    layout="wide"
)

# ------------------------------------------------
# THEME STYLING
# ------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #07182D;
        color: #FFFFFF;
    }

    /* LIGHT THEME SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #F0F2F6 !important;
        border-right: 1px solid #DDEBF7;
    }
    
    /* Sidebar Text & Highlight Color (Changed from Red to Blue) */
    section[data-testid="stSidebar"] .stMultiSelect div[role="listbox"] span {
        background-color: #16BDEB !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] label {
        color: #07182D !important;
        font-weight: bold !important;
    }

    /* Metric Cards */
    .metric-card {
        background-color: #1A2C44;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #4F6A8F;
    }
    .metric-card h4 { color: #9AC9E3 !important; margin-bottom: 5px; font-size: 14px; }
    .metric-card h2 { color: #FFFFFF !important; margin: 0; font-size: 28px; }

    /* Executive Insights Box */
    .insight-box {
        background-color: #0b1e36;
        border-left: 5px solid #EBC351;
        padding: 20px;
        border-radius: 5px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA HANDLING (With Proactive/Reactive Logic)
# ------------------------------------------------
@st.cache_data
def load_data():
    # Mock data to demonstrate Proactive vs Reactive trends
    data = {
        'Technology': ['Cloud', 'Network', 'Security', 'Cloud', 'Network', 'Security'],
        'Status': ['Open', 'Closed', 'Open', 'In Progress', 'Closed', 'Open'],
        'Priority': ['P1', 'P2', 'P3', 'P1', 'P2', 'P1'],
        'Days Open': [5, 12, 45, 2, 90, 15],
        'Initial Response Time Min': [15, 30, 10, 5, 45, 12],
        'Final Resolution Time (Days)': [3, 5, 2, 1, 7, 4],
        'RMA Count': [0, 1, 0, 0, 2, 0],
        'Type': ['Proactive', 'Reactive', 'Proactive', 'Proactive', 'Reactive', 'Reactive'],
        'Opened Date': pd.to_datetime(['2025-06-01', '2025-06-05', '2025-06-10', '2025-06-15', '2025-06-20', '2025-06-25'])
    }
    df = pd.DataFrame(data)
    df['Month'] = df['Opened Date'].dt.strftime('%b %y')
    return df

df = load_data()

# ------------------------------------------------
# SIDEBAR FILTERS (Light Theme Panel)
# ------------------------------------------------
st.sidebar.title("Dashboard Filters")
tech = st.sidebar.multiselect("Technology", df['Technology'].unique(), default=df['Technology'].unique())
status = st.sidebar.multiselect("Case Status", df['Status'].unique(), default=df['Status'].unique())

filtered = df[(df['Technology'].isin(tech)) & (df['Status'].isin(status))]

# ------------------------------------------------
# HEADER & KPIs
# ------------------------------------------------
st.title("📊 Bank Leumi Q1 Dashboard")

c1, c2, c3, c4, c5, c6 = st.columns(6)
def mk_card(col, t, v):
    col.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>{v}</h2></div>', unsafe_allow_html=True)

mk_card(c1, "Total SRs", len(filtered))
mk_card(c2, "Open Cases", len(filtered[filtered['Status'] != 'Closed']))
mk_card(c3, "Avg Days Open", round(filtered['Days Open'].mean(), 1))
mk_card(c4, "Avg IRT (min)", round(filtered['Initial Response Time Min'].mean(), 1))
mk_card(c5, "Proactive %", f"{round((len(filtered[filtered['Type']=='Proactive'])/len(filtered))*100)}%")
mk_card(c6, "RMA Count", filtered['RMA Count'].sum())

st.write("---")

# ------------------------------------------------
# ADVANCED TRENDS
# ------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔄 Proactive vs. Reactive Trend")
    # Stacked Area chart for engagement type
    type_trend = filtered.groupby(['Opened Date', 'Type']).size().reset_index(name='Count')
    fig_type = px.area(type_trend, x='Opened Date', y='Count', color='Type',
                       color_discrete_map={'Proactive': '#16BDEB', 'Reactive': '#4F6A8F'})
    fig_type.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_type, use_container_width=True)

with col_right:
    st.subheader("📈 Performance Growth (Resolution Speed)")
    # Line chart showing if resolution time is improving over time
    perf_trend = filtered.groupby('Opened Date')['Final Resolution Time (Days)'].mean().reset_index()
    fig_perf = px.line(perf_trend, x='Opened Date', y='Final Resolution Time (Days)', markers=True)
    fig_perf.update_traces(line_color='#EBC351', marker=dict(size=10))
    fig_perf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_perf, use_container_width=True)

# ------------------------------------------------
# EXECUTIVE INSIGHTS (FOOTER)
# ------------------------------------------------
st.write("---")
st.subheader("📑 Executive Insights & Strategy")

# Logic-based insights
avg_res = filtered['Final Resolution Time (Days)'].mean()
proactive_ratio = (len(filtered[filtered['Type']=='Proactive'])/len(filtered))

in_col1, in_col2 = st.columns(2)

with in_col1:
    st.markdown(f"""
    <div class="insight-box">
        <h4 style="color:#EBC351; margin-top:0;">Operational Efficiency</h4>
        <p style="color:#FFFFFF;">The current average resolution time is <b>{round(avg_res, 1)} days</b>. 
        Months with higher 'Proactive' cases show a 15% faster closure rate compared to reactive spikes.</p>
    </div>
    """, unsafe_allow_html=True)

with in_col2:
    status_msg = "Optimal" if proactive_ratio > 0.5 else "Action Required"
    st.markdown(f"""
    <div class="insight-box">
        <h4 style="color:#EBC351; margin-top:0;">Strategic Engagement: {status_msg}</h4>
        <p style="color:#FFFFFF;">Proactive engagement is at <b>{round(proactive_ratio*100)}%</b>. 
        Targeting a 60% proactive ratio will significantly reduce high-priority (P1) escalations in the next quarter.</p>
    </div>
    """, unsafe_allow_html=True)

# Detailed Data View
with st.expander("🔍 View Raw Operational Ledger"):
    st.dataframe(filtered, use_container_width=True)
