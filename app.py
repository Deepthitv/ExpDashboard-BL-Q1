import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="HTOM Expert Care Operations", layout="wide")

# ------------------------------------------------
# THEME STYLING (Strict Palette + No Red)
# ------------------------------------------------
st.markdown(f"""
<style>
    /* Global App Background */
    .stApp {{ background-color: #07182D; color: #FFFFFF; }}
    
    /* SIDEBAR: LIGHT THEME & BRANDED FILTERS */
    section[data-testid="stSidebar"] {{ 
        background-color: #F0F2F6 !important; 
        border-right: 2px solid #9AC9E3;
    }}
    
    /* Remove Red Highlight from Multi-select & Widgets */
    section[data-testid="stSidebar"] .stMultiSelect div[role="listbox"] span {{
        background-color: #4F6A8F !important; /* Brand Proactive Blue */
        color: white !important;
    }}
    
    /* Change Slider/Checkbox/Radio highlights to Brand Cyan */
    .stSlider [data-baseweb="slider"] div {{ background-color: #16BDEB !important; }}
    
    /* Sidebar Headers & Labels */
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: #07182D !important;
        font-size: 1.2rem !important;
        margin-bottom: 5px !important;
    }}
    section[data-testid="stSidebar"] label {{
        color: #1A2C44 !important;
        font-weight: 600 !important;
    }}

    /* KPI Metric Cards */
    .metric-card {{
        background-color: #1A2C44; padding: 20px; border-radius: 12px;
        text-align: center; border: 1px solid #4F6A8F;
    }}
    .metric-card h4 {{ color: #9AC9E3 !important; margin-bottom: 5px; font-size: 14px; }}
    .metric-card h2 {{ color: #FFFFFF !important; margin: 0; font-size: 28px; }}

    /* Brand Gold Titles */
    h1, h2, h3 {{ color: #EBC351 !important; font-weight: bold !important; }}

    .insight-box {{
        background-color: #1A2C44; border-left: 5px solid #EBC351;
        padding: 20px; border-radius: 5px; margin-top: 20px;
    }}

    /* Table Formatting */
    [data-testid="stTable"] td, [data-testid="stTable"] th {{
        color: #FFFFFF !important; background-color: #07182D !important;
        border: 1px solid #4F6A8F !important;
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA HANDLING
# ------------------------------------------------
@st.cache_data
def load_data():
    data = [
        {"Month": "June'25", "SR": 38, "P1/P2": 9, "IST": 4, "MTTC": 17, "Proactive": 16, "Tech": "Cloud"},
        {"Month": "July'25", "SR": 24, "P1/P2": 5, "IST": 5, "MTTC": 19, "Proactive": 7, "Tech": "Security"},
        {"Month": "Aug'25", "SR": 30, "P1/P2": 8, "IST": 4, "MTTC": 18, "Proactive": 14, "Tech": "Network"},
        {"Month": "Sep'25", "SR": 43, "P1/P2": 3, "IST": 2, "MTTC": 15, "Proactive": 28, "Tech": "Cloud"},
        {"Month": "Oct'25", "SR": 60, "P1/P2": 8, "IST": 2, "MTTC": 15, "Proactive": 22, "Tech": "Security"},
        {"Month": "Nov'25", "SR": 52, "P1/P2": 13, "IST": 2, "MTTC": 19, "Proactive": 32, "Tech": "Network"}
    ]
    df = pd.DataFrame(data)
    df['Reactive'] = df['SR'] - df['Proactive']
    df['Proactive_Pct'] = (df['Proactive'] / df['SR']) * 100
    df['Efficiency_Score'] = (1 / df['MTTC']) * 100
    return df

df = load_data()

# ------------------------------------------------
# SIDEBAR: MEANINGFUL FILTERS
# ------------------------------------------------
st.sidebar.title("🛠️ Control Center")

st.sidebar.subheader("Time Horizon")
sel_months = st.sidebar.multiselect("Select Reporting Months", df['Month'].unique(), default=df['Month'].unique())

st.sidebar.subheader("Operational Scope")
sel_tech = st.sidebar.multiselect("Technology Vertical", df['Tech'].unique(), default=df['Tech'].unique())

st.sidebar.subheader("SLA Thresholds")
max_mttc = st.sidebar.slider("Max MTTC (Days) Limit", 10, 25, 20)

# Apply Filters
filtered = df[
    (df['Month'].isin(sel_months)) & 
    (df['Tech'].isin(sel_tech)) & 
    (df['MTTC'] <= max_mttc)
].copy()

# ------------------------------------------------
# MAIN DASHBOARD
# ------------------------------------------------
st.title("📊 HTOM Expert Care Operations Dashboard")

# KPI ROW
c1, c2, c3, c4, c5, c6 = st.columns(6)
def mk_card(col, t, v):
    col.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>{v}</h2></div>', unsafe_allow_html=True)

mk_card(c1, "Total SRs", filtered["SR"].sum())
mk_card(c2, "Avg IST", f'{round(filtered["IST"].mean(), 1)}h')
mk_card(c3, "Avg MTTC", f'{round(filtered["MTTC"].mean(), 1)}d')
mk_card(c4, "Proactive %", f"{round(filtered['Proactive_Pct'].mean())}%")
mk_card(c5, "P1/P2 Load", filtered["P1/P2"].sum())
mk_card(c6, "Efficiency", round(filtered["Efficiency_Score"].mean(), 1))

st.divider()

# ------------------------------------------------
# TRENDS & ANALYSIS
# ------------------------------------------------
st.header("Operational Metrics & Bottleneck Analysis")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Monthly Engagement Composition")
    fig_share = px.bar(filtered, x="Month", y=["Proactive", "Reactive"],
                       color_discrete_map={"Proactive": "#4F6A8F", "Reactive": "#9AC9E3"})
    fig_share.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_share, use_container_width=True)

with col_b:
    st.subheader("Efficiency Heatmap")
    heat_df = filtered.set_index('Month')[['IST', 'MTTC']].T
    fig_heat = px.imshow(heat_df, color_continuous_scale=['#4F6A8F', '#9AC9E3', '#EBC351'])
    fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_heat, use_container_width=True)

st.header("Performance & Growth Trends")
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("MTTC Improvement Trend")
    fig_growth = px.line(filtered, x="Month", y="MTTC", markers=True, color_discrete_sequence=["#EBC351"])
    fig_growth.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_growth, use_container_width=True)

with col_d:
    st.subheader("Proactive Capture Trend")
    fig_pct = px.area(filtered, x="Month", y="Proactive_Pct", color_discrete_sequence=["#4F6A8F"])
    fig_pct.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_pct, use_container_width=True)

# ------------------------------------------------
# LEDGERS
# ------------------------------------------------
st.header("Detailed Performance Ledger")
def brand_color_status(row):
    if row['MTTC'] > 18: return "Attention"
    elif row['Proactive_Pct'] > 50: return "Optimal"
    else: return "Stable"

filtered['Status'] = filtered.apply(brand_color_status, axis=1)

def apply_brand_colors(val):
    colors = {"Attention": "#4F6A8F", "Optimal": "#EBC351", "Stable": "#1A2C44"}
    return f'background-color: {colors.get(val, "#1A2C44")}; color: white; font-weight: bold'

st.dataframe(filtered[['Month', 'Status', 'SR', 'IST', 'MTTC', 'Proactive_Pct']].style.applymap(apply_brand_colors, subset=['Status']), use_container_width=True)

st.header("Initial Raw Data Table")
st.table(filtered[['Month', 'SR', 'P1/P2', 'IST', 'MTTC', 'Proactive']])

# ------------------------------------------------
# EXECUTIVE INSIGHTS
# ------------------------------------------------
st.header("Executive Insights")
ins_1, ins_2 = st.columns(2)

with ins_1:
    st.markdown(f"""<div class="insight-box">
    <h4>Engagement Strategy</h4>
    <p>Filtered data shows a proactive rate of <b>{round(filtered['Proactive_Pct'].mean())}%</b>. 
    Increasing the volume in <b>{sel_tech}</b> verticals is expected to improve overall resolution efficiency.</p></div>""", unsafe_allow_html=True)

with ins_2:
    st.markdown(f"""<div class="insight-box">
    <h4>SLA Compliance</h4>
    <p>Average MTTC is currently <b>{round(filtered['MTTC'].mean(), 1)} days</b>. 
    No severe bottlenecks are present within the current {max_mttc}-day filter threshold.</p></div>""", unsafe_allow_html=True)
