import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="AI Usage Trends",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0a0a14;
        color: #e0e0f0;
    }
    .main { background-color: #0a0a14; }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: #a78bfa;
    }

    .stMetric {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #a78bfa33;
        border-radius: 12px;
        padding: 1rem;
    }

    .stMetric label { color: #a0a0c0 !important; font-size: 0.8rem; }
    .stMetric div[data-testid="metric-container"] > div { color: #a78bfa !important; }

    .section-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.1rem;
        color: #a78bfa;
        border-left: 4px solid #a78bfa;
        padding-left: 12px;
        margin: 2rem 0 1rem 0;
    }

    .stSidebar { background-color: #0f0f1f !important; }
    .stSidebar [data-testid="stSidebarContent"] { background-color: #0f0f1f; }

    .chart-note {
        font-size: 0.78rem;
        color: #6060a0;
        margin-top: -0.5rem;
        margin-bottom: 1rem;
        font-style: italic;
    }

    footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("AI_tools_dataset.csv")
    df["date"] = pd.to_datetime(df["date"])

    tools = []
    for col in df.columns:
        if "_global_users" in col or col == "Tongyi_users":
            tool = "Tongyi" if col == "Tongyi_users" else col.replace("_global_users", "")
            revenue_col = f"{tool}_revenue_usd"
            market_col  = f"{tool}_market_share_pct"

            temp = pd.DataFrame({
                "tool_name"   : tool,
                "users"       : df[col],
                "revenue"     : df[revenue_col] if revenue_col in df.columns else 0,
                "market_share": df[market_col]  if market_col  in df.columns else 0,
                "date"        : df["date"],
                "year"        : df["date"].dt.year,
            })
            tools.append(temp)

    final_df = pd.concat(tools, ignore_index=True)
    final_df["tool_name"] = final_df["tool_name"].replace({
        "GrammarlyAI"    : "Grammarly",
        "CopyAI"         : "Copy.ai",
        "JasperAI"       : "Jasper AI",
        "GitHubCopilot"  : "GitHub Copilot",
        "StableDiffusion": "Stable Diffusion",
        "ERNIE"          : "ERNIE (Baidu)",
    })
    return final_df[final_df["users"] > 0].copy()

df = load_data()

# ---------------- PLOTLY BASE THEME ----------------
BASE = dict(
    template="plotly_dark",
    paper_bgcolor="#0a0a14",
    plot_bgcolor="#0f0f1f",
    font=dict(family="Inter", color="#c0c0e0"),
)

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("<h2 style='font-family:Orbitron;font-size:1rem;color:#a78bfa;'>⚙️ Controls</h2>",
                    unsafe_allow_html=True)

all_tools  = sorted(df["tool_name"].unique())
sel_tools  = st.sidebar.multiselect("Select AI Tools", all_tools, default=all_tools)
years      = sorted(df["year"].unique())
year_range = st.sidebar.slider("Year Range", int(min(years)), int(max(years)),
                               (int(min(years)), int(max(years))))

fdf = df[df["tool_name"].isin(sel_tools) & df["year"].between(year_range[0], year_range[1])]

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;font-size:2.2rem;'>🤖 AI USAGE TRENDS</h1>",
            unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6060a0;margin-top:-0.5rem;'>Global AI Tool Adoption · 2016 – 2026</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ---------------- METRICS ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Users",   f"{int(fdf['users'].sum()):,}")
c2.metric("Peak Daily",    f"{int(fdf['users'].max()):,}")
c3.metric("Tools Tracked", fdf["tool_name"].nunique())
c4.metric("Years of Data", f"{year_range[0]} – {year_range[1]}")
st.markdown("---")

# ══════════════════════════════════════════
# 1. LINE — User Growth Over Time
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>📈 LINE CHART — User Growth Over Time</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Shows how each AI tool's daily active users grew from launch to present.</p>",
            unsafe_allow_html=True)

monthly = fdf.groupby(["date", "tool_name"], as_index=False)["users"].mean()
fig1 = px.line(monthly, x="date", y="users", color="tool_name",
               labels={"date": "Date", "users": "Global Users", "tool_name": "AI Tool"},
               title="Global User Growth by AI Tool")
fig1.update_layout(**BASE, hovermode="x unified",
                   height=600,
                   xaxis=dict(rangeslider=dict(visible=True)))
fig1.update_xaxes(fixedrange=False)
fig1.update_yaxes(fixedrange=False)
st.plotly_chart(fig1, use_container_width=True)

# ══════════════════════════════════════════
# 2. BAR — Yearly Average Users (grouped)
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>📊 BAR CHART — Average Users Per Year by Tool</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Compares average daily users each year across selected tools.</p>",
            unsafe_allow_html=True)

yearly_avg = fdf.groupby(["year", "tool_name"], as_index=False)["users"].mean()
fig2 = px.bar(yearly_avg, x="year", y="users", color="tool_name", barmode="group",
              labels={"year": "Year", "users": "Avg Daily Users", "tool_name": "AI Tool"},
              title="Year-wise Average Users per AI Tool")
fig2.update_layout(**BASE)
st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════
# 3. PIE — Market Share Snapshot
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>🥧 PIE CHART — Current Market Share</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Distribution of market share among AI tools at the latest available date.</p>",
            unsafe_allow_html=True)

latest = fdf["date"].max()
pie_df = fdf[fdf["date"] == latest].groupby("tool_name", as_index=False)["market_share"].mean()
pie_df = pie_df[pie_df["market_share"] > 0]

fig3 = px.pie(pie_df, names="tool_name", values="market_share", hole=0.35,
              title=f"Market Share as of {latest.strftime('%B %Y')}")
fig3.update_layout(**BASE)
st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════
# 4. SCATTER — Users vs Market Share
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>🔵 SCATTER CHART — Users vs Market Share</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Each dot = one tool on one day. Shows whether more users = more market share.</p>",
            unsafe_allow_html=True)

scatter_df = fdf[fdf["market_share"] > 0].sample(min(5000, len(fdf)), random_state=42)
fig4 = px.scatter(scatter_df, x="users", y="market_share", color="tool_name",
                  size="users", size_max=18, opacity=0.7,
                  labels={"users": "Global Users", "market_share": "Market Share (%)",
                          "tool_name": "AI Tool"},
                  title="Users vs Market Share per Tool")
fig4.update_layout(**BASE, dragmode="zoom")
fig4.update_xaxes(fixedrange=False)
fig4.update_yaxes(fixedrange=False)
st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════
# 5. HISTOGRAM — Daily User Distribution
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>📉 HISTOGRAM — Daily User Distribution</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>How spread out are daily user counts? Shows what's typical vs extreme.</p>",
            unsafe_allow_html=True)

fig5 = px.histogram(fdf, x="users", color="tool_name", nbins=40,
                    barmode="overlay", opacity=0.7,
                    labels={"users": "Daily Users", "tool_name": "AI Tool"},
                    title="Distribution of Daily User Counts by Tool")
fig5.update_layout(**BASE)
st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════
# 6. HEATMAP — Users per Tool per Year
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>🔥 HEATMAP — Avg Users per Tool per Year</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Intensity of color = more users. Quickly spot which tool dominated each year.</p>",
            unsafe_allow_html=True)

heat_df    = fdf.groupby(["year", "tool_name"], as_index=False)["users"].mean()
heat_pivot = heat_df.pivot(index="tool_name", columns="year", values="users").fillna(0)

fig6 = go.Figure(data=go.Heatmap(
    z=heat_pivot.values,
    x=[str(c) for c in heat_pivot.columns],
    y=heat_pivot.index.tolist(),
    colorscale="Purples",
    hoverongaps=False,
    colorbar=dict(title="Avg Users")
))
fig6.update_layout(**BASE,
    title="Heatmap: Average Daily Users per Tool per Year",
    xaxis_title="Year",
    yaxis_title="AI Tool",
    height=500
)
st.plotly_chart(fig6, use_container_width=True)

# ══════════════════════════════════════════
# 7. HORIZONTAL BAR — Peak Users Ranking
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>🏆 HORIZONTAL BAR — Peak Users Ranking</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Which AI tool ever hit the highest user count? Ranked comparison.</p>",
            unsafe_allow_html=True)

peak = fdf.groupby("tool_name", as_index=False)["users"].max().sort_values("users")
fig7 = px.bar(peak, x="users", y="tool_name", orientation="h",
              color="users", color_continuous_scale="Purples",
              labels={"users": "Peak Global Users", "tool_name": "AI Tool"},
              title="All-Time Peak Users per AI Tool")
fig7.update_layout(**BASE)
st.plotly_chart(fig7, use_container_width=True)

# ══════════════════════════════════════════
# 8. LINE — Market Share Over Time
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>📉 LINE CHART — Market Share Trends</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>Tracks how each tool's share of the AI market shifted over time.</p>",
            unsafe_allow_html=True)

ms_df = fdf[fdf["market_share"] > 0].groupby(["date", "tool_name"], as_index=False)["market_share"].mean()
fig8  = px.line(ms_df, x="date", y="market_share", color="tool_name",
                labels={"date": "Date", "market_share": "Market Share (%)", "tool_name": "AI Tool"},
                title="Market Share (%) Over Time")
fig8.update_layout(**BASE, hovermode="x unified",
                   xaxis=dict(rangeslider=dict(visible=True)))
fig8.update_xaxes(fixedrange=False)
fig8.update_yaxes(fixedrange=False)
st.plotly_chart(fig8, use_container_width=True)

# ══════════════════════════════════════════
# 9. AREA — Total AI Ecosystem Growth
# ══════════════════════════════════════════
st.markdown("<div class='section-title'>🌍 AREA CHART — Total AI Ecosystem Growth</div>",
            unsafe_allow_html=True)
st.markdown("<p class='chart-note'>The combined user base of all selected AI tools growing over time.</p>",
            unsafe_allow_html=True)

total = fdf.groupby("date", as_index=False)["users"].sum()
fig9  = px.area(total, x="date", y="users",
                labels={"date": "Date", "users": "Total Global Users"},
                title="Combined AI Tool Users Over Time",
                color_discrete_sequence=["#a78bfa"])
fig9.update_layout(**BASE, xaxis=dict(rangeslider=dict(visible=True)))
fig9.update_xaxes(fixedrange=False)
fig9.update_yaxes(fixedrange=False)
st.plotly_chart(fig9, use_container_width=True)

# ---------------- RAW DATA ----------------
st.markdown("<div class='section-title'>🗂️ Raw Data Preview</div>", unsafe_allow_html=True)
st.dataframe(fdf.sort_values("date", ascending=False).head(100), use_container_width=True)

st.markdown("---")
st.markdown("<p style='text-align:center;color:#404060;font-size:0.75rem;'>Data source: AI_tools_dataset.csv &nbsp;|&nbsp; Built with Streamlit & Plotly</p>",
            unsafe_allow_html=True)
