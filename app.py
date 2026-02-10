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
# THEME STYLING (Custom Palette Integration)
# ------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #07182D;
        color: #FFFFFF;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b1e36;
    }

    /* Typography */
    h1, h2, h3 {
        color: #EBC351 !important; /* Gold Accent */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h4 {
        color: #9AC9E3 !important; /* Light Blue Subheaders */
        font-weight: 400;
    }

    /* Metric Card Styling */
    .metric-card {
        background-color: #1A2C44; /* Lighter Blue Card */
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #4F6A8F; /* Muted Blue Border */
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #EBC351;
    }

    .metric-card h4 {
        margin: 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .metric-card h2 {
        margin: 10px 0 0 0;
        font-size: 2rem;
        color: #FFFFFF !important;
    }

    /* Global Text Clarity */
    p, label {
        color: #9AC9E3 !important;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA HANDLING (Placeholder logic from your code)
# ------------------------------------------------
@st.cache_data
def load_data():
    # Attempting to mimic your load structure with sample data for rendering
    data = {
        'Technology': ['Cloud', 'Network', 'Security', 'Cloud', 'Network'],
        'Status': ['Open', 'Closed', 'Open', 'In Progress', 'Closed'],
        'Priority - Current (Text)': ['P1', 'P2', 'P3', 'P1', 'P2'],
        'Days Open': [5, 12, 45, 2, 90],
        'Initial Response Time Min': [15, 30, 10, 5, 45],
        'Final Resolution Time (Days)': [3, 5, 2, 1, 7],
        'RMA Count': [0, 1, 0, 0, 2],
        'Opened Date': pd.to_datetime(['2025-06-01', '2025-06-05', '2025-06-10', '2025-06-15', '2025-06-20'])
    }
    return pd.DataFrame(data)

df = load_data()

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------
st.sidebar.title("🔍 Operations Filters")
tech = st.sidebar.multiselect("Technology", df['Technology'].unique(), default=df['Technology'].unique())
status = st.sidebar.multiselect("Status", df['Status'].unique(), default=df['Status'].unique())
priority = st.sidebar.multiselect("Priority", df['Priority - Current (Text)'].unique(), default=df['Priority - Current (Text)'].unique())

filtered = df[(df['Technology'].isin(tech)) & (df['Status'].isin(status)) & (df['Priority - Current (Text)'].isin(priority))]

# ------------------------------------------------
# KPI CALCULATIONS
# ------------------------------------------------
total_cases = len(filtered)
open_cases = len(filtered[filtered['Status'] != "Closed"])
avg_days_open = filtered['Days Open'].mean()
avg_irt = filtered['Initial Response Time Min'].mean()
avg_res = filtered['Final Resolution Time (Days)'].mean()
total_rma = filtered['RMA Count'].sum()

# ------------------------------------------------
# HEADER & KPI ROW
# ------------------------------------------------
st.title("📊 Bank Leumi Q1 Dashboard")

c1, c2, c3, c4, c5, c6 = st.columns(6)

def metric_card(col, title, value):
    col.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

metric_card(c1, "Total SRs", total_cases)
metric_card(c2, "Open Cases", open_cases)
metric_card(c3, "Avg Days Open", round(avg_days_open, 1))
metric_card(c4, "Avg IRT (min)", round(avg_irt, 1))
metric_card(c5, "Resolution", f"{round(avg_res, 1)}d")
metric_card(c6, "Total RMA", int(total_rma))

st.write("---")

# ------------------------------------------------
# VISUALIZATIONS
# ------------------------------------------------
col1, col2 = st.columns(2)

# Case Status Distribution
with col1:
    st.subheader("📌 Case Status Distribution")
    status_fig = px.pie(
        filtered, names='Status', 
        color_discrete_sequence=["#4F6A8F", "#9AC9E3", "#EBC351"]
    )
    status_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF", showlegend=True
    )
    st.plotly_chart(status_fig, use_container_width=True)

# Technology Load
with col2:
    st.subheader("💻 Technology Distribution")
    tech_counts = filtered['Technology'].value_counts().reset_index()
    tech_fig = px.bar(
        tech_counts, x='count', y='Technology', orientation='h',
        color_discrete_sequence=["#4F6A8F"]
    )
    tech_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FFFFFF", xaxis_title="Case Volume", yaxis_title=""
    )
    st.plotly_chart(tech_fig, use_container_width=True)

# Trend Line
st.subheader("📈 Case Creation Trend")
trend = filtered.groupby(filtered['Opened Date'].dt.date).size().reset_index(name='Cases')
trend_fig = px.line(trend, x='Opened Date', y='Cases', color_discrete_sequence=["#EBC351"])
trend_fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#FFFFFF", xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#1A2C44")
)
st.plotly_chart(trend_fig, use_container_width=True)

# ------------------------------------------------
# RISK DATA TABLE
# ------------------------------------------------
st.subheader("📋 Detailed Operational Ledger")
# Applying a high-contrast style to the dataframe
st.dataframe(filtered.style.set_properties(**{
    'background-color': '#1A2C44',
    'color': '#FFFFFF',
    'border-color': '#4F6A8F'
}), use_container_width=True)
