import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------
st.set_page_config(page_title="Bank Leumi FY26 Quarter_1 Dashboard", layout="wide")

# ------------------------------------------------
# THEME STYLING (Preserved Exactly)
# ------------------------------------------------
st.markdown(f"""
<style>
    /* Global App Background */
    .stApp {{ background-color: #07182D; color: #FFFFFF; }}
    
    /* SIDEBAR: LIGHT THEME */
    section[data-testid="stSidebar"] {{ 
        background-color: #F0F2F6 !important; 
        border-right: 2px solid #9AC9E3;
    }}
    
    /* ELIMINATE RED HIGHLIGHTS (Dropdowns & Tags) */
    span[data-baseweb="tag"] {{
        background-color: #4F6A8F !important;
        color: white !important;
    }}
    div[data-baseweb="select"] > div:focus-within {{
        border-color: #16BDEB !important;
    }}
    li[role="option"][aria-selected="true"] {{
        background-color: #9AC9E3 !important;
    }}

    /* Sidebar Labels */
    section[data-testid="stSidebar"] label {{
        color: #1A2C44 !important;
        font-weight: 600 !important;
    }}

    /* METRIC CARDS: Forced Lighter Background (#1A2C44) */
    .metric-card {{
        background-color: #1A2C44 !important; 
        padding: 20px; 
        border-radius: 12px;
        text-align: center; 
        border: 1px solid #4F6A8F;
        margin-bottom: 10px;
    }}
    .metric-card h4 {{ color: #9AC9E3 !important; margin: 0; font-size: 14px; }}
    .metric-card h2 {{ color: #FFFFFF !important; margin: 5px 0 0 0; font-size: 28px; }}

    /* INSIGHT BOX: Forced Lighter Background (#1A2C44) */
    .insight-box {{
        background-color: #1A2C44 !important; 
        border-left: 5px solid #EBC351;
        padding: 20px; 
        border-radius: 5px; 
        margin-top: 20px;
    }}

    /* TITLES: Gold (#EBC351) */
    h1, h2, h3 {{ color: #EBC351 !important; font-weight: bold !important; }}

    /* RAW DATA TABLE: Explicit White Font & Dark Background */
    [data-testid="stTable"] {{
        background-color: #07182D !important;
        color: #FFFFFF !important;
    }}
    [data-testid="stTable"] thead tr th {{
        color: #EBC351 !important; 
        background-color: #1A2C44 !important;
    }}
    [data-testid="stTable"] tbody tr td {{
        color: #FFFFFF !important;
        background-color: #07182D !important;
        border-bottom: 1px solid #4F6A8F !important;
    }}

    /* PDF BUTTON STYLING */
    .stButton>button {{
        background-color: #4F6A8F !important;
        color: white !important;
        border: 1px solid #9AC9E3 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA HANDLING (Updated to Bucket Real CSV Data)
# ------------------------------------------------
@st.cache_data
def load_data():
    if not os.path.exists("cases.csv"):
        return pd.DataFrame()
    
    # Load raw data
    raw_df = pd.read_csv("cases.csv")
    
    # 1. Bucket by Month using 'Opened Date'
    raw_df['Opened Date'] = pd.to_datetime(raw_df['Opened Date'])
    raw_df['Month_Sort'] = raw_df['Opened Date'].dt.to_period('M') # For chronological sorting
    raw_df['Month'] = raw_df['Opened Date'].dt.strftime('%b\'%y')
    
    # 2. Extract Key Metrics
    raw_df['SR_Count'] = 1
    raw_df['MTTC_Val'] = pd.to_numeric(raw_df['Final Resolution Time (Days)'], errors='coerce').fillna(0)
    raw_df['IST_Val'] = pd.to_numeric(raw_df['IST Hours'], errors='coerce').fillna(0)
    raw_df['P1P2_Val'] = raw_df['Priority - Current (Text)'].apply(lambda x: 1 if str(x) in ['1', '2'] else 0)
    raw_df['Is_Proactive'] = raw_df['ContractTitle'].str.contains('ProActive', case=False, na=False).astype(int)
    
    # 3. Group by Month and Technology to create the dashboard dataframe
    df = raw_df.groupby(['Month', 'Month_Sort', 'Technology']).agg({
        'SR_Count': 'sum',
        'P1P2_Val': 'sum',
        'IST_Val': 'mean',
        'MTTC_Val': 'mean',
        'Is_Proactive': 'sum'
    }).reset_index()
    
    # 4. Rename columns to match existing app logic
    df.columns = ['Month', 'Month_Sort', 'Tech', 'SR', 'P1/P2', 'IST', 'MTTC', 'Proactive']
    
    # Sort by date so trends look correct
    df = df.sort_values('Month_Sort').drop(columns=['Month_Sort'])
    
    # 5. Final Dashboard Calculations
    df['Reactive'] = df['SR'] - df['Proactive']
    df['Proactive_Pct'] = (df['Proactive'] / df['SR']) * 100
    df['Efficiency_Score'] = df['MTTC'].apply(lambda x: (1/x)*100 if x > 0 else 0)
    
    return df

df = load_data()

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------
st.sidebar.title("🛠️ Control Center")
if not df.empty:
    sel_months = st.sidebar.multiselect("Reporting Months", df['Month'].unique(), default=df['Month'].unique())
    sel_tech = st.sidebar.multiselect("Technology Vertical", df['Tech'].unique(), default=df['Tech'].unique())

    filtered = df[(df['Month'].isin(sel_months)) & (df['Tech'].isin(sel_tech))].copy()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Report Export")

    if st.sidebar.button("📄 Save Dashboard as PDF"):
        st.components.v1.html("<script>window.parent.print();</script>", height=0)

    csv = filtered.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="📥 Download Data (CSV)", data=csv, file_name='Bank_Leumi_Report.csv')

    # ------------------------------------------------
    # MAIN DASHBOARD
    # ------------------------------------------------
    st.title("📊 Bank Leumi FY26 Quarter_1 Dashboard")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    def mk_card(col, t, v):
        col.markdown(f'<div class="metric-card"><h4>{t}</h4><h2>{v}</h2></div>', unsafe_allow_html=True)

    mk_card(c1, "Total SRs", int(filtered["SR"].sum()))
    mk_card(c2, "Avg IST", f'{round(filtered["IST"].mean(), 1)}h')
    mk_card(c3, "Avg MTTC", f'{round(filtered["MTTC"].mean(), 1)}d')
    mk_card(c4, "Proactive %", f"{round(filtered['Proactive_Pct'].mean())}%")
    mk_card(c5, "P1/P2 Load", int(filtered["P1/P2"].sum()))
    mk_card(c6, "Efficiency", round(filtered["Efficiency_Score"].mean(), 1))

    st.divider()

    # TRENDS
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Monthly Engagement Share")
        fig1 = px.bar(filtered, x="Month", y=["Proactive", "Reactive"], color_discrete_map={"Proactive": "#4F6A8F", "Reactive": "#9AC9E3"})
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        st.subheader("Efficiency Heatmap")
        heat_df = filtered.set_index('Month')[['IST', 'MTTC']].T
        fig2 = px.imshow(heat_df, color_continuous_scale=['#4F6A8F', '#9AC9E3', '#EBC351'])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
        st.plotly_chart(fig2, use_container_width=True)

    st.header("Performance & Growth Trends")
    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("MTTC Improvement Trend")
        fig3 = px.line(filtered, x="Month", y="MTTC", markers=True, color_discrete_sequence=["#EBC351"])
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
        st.plotly_chart(fig3, use_container_width=True)
    with col_d:
        st.subheader("Proactive Capture Trend")
        fig4 = px.area(filtered, x="Month", y="Proactive_Pct", color_discrete_sequence=["#4F6A8F"])
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#FFFFFF")
        st.plotly_chart(fig4, use_container_width=True)

    # PERFORMANCE LEDGER
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

    # INITIAL RAW DATA TABLE
    st.header("Initial Raw Data Table")
    st.table(filtered[['Month', 'SR', 'P1/P2', 'IST', 'MTTC', 'Proactive']])

    # EXECUTIVE INSIGHTS
    st.header("Executive Insights")
    in1, in2 = st.columns(2)
    with in1:
        st.markdown(f'<div class="insight-box"><h4>Engagement Strategy</h4><p>Proactive rate is <b>{round(filtered["Proactive_Pct"].mean())}%</b>. Preventive care is reducing reactive tickets.</p></div>', unsafe_allow_html=True)
    with in2:
        st.markdown(f'<div class="insight-box"><h4>Efficiency Growth</h4><p>Avg MTTC is <b>{round(filtered["MTTC"].mean(), 1)} days</b>. Trends are within health targets.</p></div>', unsafe_allow_html=True)
else:
    st.error("No data found. Please ensure 'cases.csv' is in your GitHub repository.")
