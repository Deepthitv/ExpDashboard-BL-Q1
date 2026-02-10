import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="HTOM Expert Care Operations", layout="wide")

# ------------------------------------------------
# THEME STYLING (Strict Palette Adherence)
# ------------------------------------------------
st.markdown(f"""
<style>
    /* Global Background and Text */
    .stApp {{ 
        background-color: #07182D; 
        color: #FFFFFF; 
    }}
    
    /* LIGHT THEME SIDEBAR */
    section[data-testid="stSidebar"] {{ 
        background-color: #F0F2F6 !important; 
    }}
    section[data-testid="stSidebar"] .stMultiSelect div[role="listbox"] span {{
        background-color: #4F6A8F !important; /* Brand Proactive Blue */
        color: white !important;
    }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] label {{
        color: #07182D !important; 
        font-weight: bold !important;
    }}

    /* Metric Cards (Card Background: #1A2C44) */
    .metric-card {{
        background-color: #1A2C44; 
        padding: 20px; 
        border-radius: 12px;
        text-align: center; 
        border: 1px solid #4F6A8F;
    }}
    .metric-card h4 {{ color: #9AC9E3 !important; margin-bottom: 5px; font-size: 14px; }}
    .metric-card h2 {{ color: #FFFFFF !important; margin: 0; font-size: 28px; }}

    /* Gold Titles (#EBC351) */
    h1, h2, h3 {{
        color: #EBC351 !important;
        font-weight: bold !important;
    }}

    /* Executive Insights Box */
    .insight-box {{
        background-color: #1A2C44; 
        border-left: 5px solid #EBC351;
        padding: 20px; 
        border-radius: 5px; 
        margin-top: 20px;
    }}

    /* High Contrast Table Fix */
    [data-testid="stTable"] td, [data-testid="stTable"] th {{
        color: #FFFFFF !important; 
        background-color: #07182D !important;
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
        {"Month": "June'25", "SR": 38, "P1/P2": 9, "IST": 4, "Impacting": 0, "MTTC": 17, "Proactive": 16},
        {"Month": "July'25", "SR": 24, "P1/P2": 5, "IST": 5, "Impacting": 1, "MTTC": 19, "Proactive": 7},
        {"Month": "Aug'25", "SR": 30, "P1/P2": 8, "IST": 4, "Impacting": 1, "MTTC": 18, "Proactive": 14},
        {"Month": "Sep'25", "SR": 43, "P1/P2": 3, "IST": 2, "Impacting": 0, "MTTC": 15, "Proactive": 28},
        {"Month": "Oct'25", "SR": 60, "P1/P2": 8, "IST": 2, "Impacting": 0, "MTTC": 15, "Proactive": 22},
        {"Month": "Nov'25", "SR": 52, "P1/P2": 13, "IST": 2, "Impacting": 0, "MTTC": 19, "Proactive": 32}
    ]
    df = pd.DataFrame(data)
    df['Reactive'] = df['SR'] - df['Proactive']
    df['Proactive_Pct'] = (df['Proactive'] / df['SR']) * 100
    return df

df = load_data()

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------
st.sidebar.title("Navigation")
sel_months = st.sidebar.multiselect("Time Period", df['Month'].unique(), default=df['Month'].unique())
filtered = df[df['Month'].isin(sel_months)].copy()

# ------------------------------------------------
# KPI SECTION
# ------------------------------------------------
st.title("📊 HTOM Expert Care Operations Dashboard")
c1, c2, c3, c4, c5, c6 = st.columns(6)

def mk_card(col, t, v):
    col.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>{v}</h2></div>', unsafe_allow_html=True)

mk_card(c1, "Total SRs", filtered["SR"].sum())
mk_card(c2, "Avg IST", f'{round(filtered["IST"].mean(), 1)}h')
mk_card(c3, "Avg MTTC", f'{round(filtered["MTTC"].mean(), 1)}d')
mk_card(c4, "Proactive %", f"{round(filtered['Proactive_Pct'].mean())}%")
mk_card(c5, "P1/P2 Total", filtered["P1/P2"].sum())
mk_card(c6, "Impacting", filtered["Impacting"].sum())

st.divider()

# ------------------------------------------------
# ANALYTICS & BOTTLENECKS
# ------------------------------------------------
st.header("Operational Metrics & Bottleneck Analysis")
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Monthly Engagement Share")
    # Using Proactive (#4F6A8F) vs Reactive (#9AC9E3)
    fig_share = px.bar(filtered, x="Month", y=["Proactive", "Reactive"],
                       color_discrete_map={"Proactive": "#4F6A8F", "Reactive": "#9AC9E3"})
    fig_share.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_share, use_container_width=True)

with col_b:
    st.subheader("Efficiency Heatmap")
    heat_df = filtered.set_index('Month')[['IST', 'MTTC']].T
    # Heatmap using Blue-to-Gold scale to stay in theme
    fig_heat = px.imshow(heat_df, color_continuous_scale=['#4F6A8F', '#9AC9E3', '#EBC351'])
    fig_heat.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
    st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------------
# PERFORMANCE LEDGERS
# ------------------------------------------------
st.header("Detailed Performance Ledger")

# Status Logic using Brand Colors (Deep Blue vs Light Blue)
def brand_color_status(row):
    if row['MTTC'] > 18: return "Attention"
    elif row['Proactive_Pct'] > 50: return "Optimal"
    else: return "Stable"

filtered['Status'] = filtered.apply(brand_color_status, axis=1)

def apply_brand_colors(val):
    if val == "Attention": color = '#4F6A8F' # Darker Blue
    elif val == "Optimal": color = '#EBC351' # Gold
    else: color = '#1A2C44' # Card Blue
    return f'background-color: {color}; color: white; font-weight: bold'

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
    <h4>Proactive Growth</h4>
    <p>Engagement quality is consistent with a <b>{round(filtered['Proactive_Pct'].mean())}%</b> proactive capture rate. 
    This aligns with the target of shifting toward preventive expert care.</p></div>""", unsafe_allow_html=True)

with ins_2:
    st.markdown(f"""<div class="insight-box">
    <h4>Throughput Efficiency</h4>
    <p>Average resolution (MTTC) is currently <b>{round(filtered['MTTC'].mean(), 1)} days</b>. 
    Slight bottlenecks observed in July and November where volume peaked.</p></div>""", unsafe_allow_html=True)
