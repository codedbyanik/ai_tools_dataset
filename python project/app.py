import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Usage Trends Dashboard", layout="wide")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("AI_tools_dataset.csv")

    dataframes = []

    for col in df.columns:
        if "global_users" in col:
            tool = col.replace("_global_users", "")

            tool_labels = {
                "deepl": "DeepL",
                "copyai": "Copy.ai",
                "jasperai": "Jasper AI",
                "githubcopilot": "GitHub Copilot"
            }
            tool_name = tool_labels.get(tool, tool.capitalize())

            users = df[col]

            revenue_col = f"{tool}_revenue_usd"
            market_col = f"{tool}_market_share_pct"

            revenue = df[revenue_col] if revenue_col in df.columns else pd.Series([0]*len(df))
            market = df[market_col] if market_col in df.columns else pd.Series([0]*len(df))

            temp = pd.DataFrame({
                "tool_name": tool_name,
                "users": users,
                "revenue": revenue,
                "market_share": market,
                "date": range(len(df))
            })

            dataframes.append(temp)

    final_df = pd.concat(dataframes, ignore_index=True)
    return final_df


df = load_data()

# ------------------ SIDEBAR ------------------
st.sidebar.title("🎛️ Controls")
tools = df['tool_name'].unique().tolist()
selected_tools = st.sidebar.multiselect("Select AI Tools", tools, default=tools)

filtered_df = df[df['tool_name'].isin(selected_tools)]

# ------------------ TITLE ------------------
st.title("🤖 AI Application Usage Trends")

# ------------------ CHECK EMPTY ------------------
if filtered_df.empty:
    st.error("No data available. Check dataset or filters.")
    st.stop()

# ------------------ METRICS ------------------
col1, col2, col3 = st.columns(3)
col1.metric("👥 Users", f"{int(filtered_df['users'].sum()):,}")
col2.metric("💰 Revenue", f"${filtered_df['revenue'].sum():,.0f}")
col3.metric("📊 Market Share", f"{filtered_df['market_share'].mean():.2f}%")

# ------------------ LINE CHART ------------------
st.subheader("📈 User Growth")
fig1 = px.line(filtered_df, x='date', y='users', color='tool_name')
st.plotly_chart(fig1, use_container_width=True)

# ------------------ BAR CHART ------------------
st.subheader("💰 Revenue Comparison")
bar_data = filtered_df.groupby('tool_name', as_index=False)['revenue'].sum()
fig2 = px.bar(bar_data, x='tool_name', y='revenue', color='tool_name')
st.plotly_chart(fig2, use_container_width=True)

# ------------------ PIE CHART ------------------
st.subheader("📊 Market Share")
pie_data = filtered_df.groupby('tool_name', as_index=False)['market_share'].mean()
fig3 = px.pie(pie_data, names='tool_name', values='market_share')
st.plotly_chart(fig3, use_container_width=True)

# ------------------ HISTOGRAM ------------------
st.subheader("📊 Distribution")
fig4 = px.histogram(filtered_df, x="users", nbins=15)
st.plotly_chart(fig4, use_container_width=True)

# ------------------ SCATTER ------------------
st.subheader("🔍 Users vs Revenue")
fig5 = px.scatter(filtered_df, x="users", y="revenue", color="tool_name")
st.plotly_chart(fig5, use_container_width=True)

# ------------------ DATA PREVIEW ------------------
st.subheader("📁 Data Preview")
st.dataframe(filtered_df.head(20))

# ------------------ FOOTER ------------------
st.markdown("---")
st.caption("Made with ❤️ using Streamlit | Fully aligned with Data Visualization syllabus")