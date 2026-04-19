import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Usage Trends", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("AI_tools_dataset.csv")

    tools = []
    for col in df.columns:
        if "_global_users" in col:
            tool = col.replace("_global_users", "")
            
            users = df[col]
            revenue = df.get(f"{tool}_revenue_usd", pd.Series([0]*len(df)))
            market = df.get(f"{tool}_market_share_pct", pd.Series([0]*len(df)))

            temp = pd.DataFrame({
                "tool_name": tool,
                "users": users,
                "revenue": revenue,
                "market_share": market,
                "date": range(len(df))
            })

            tools.append(temp)

    final_df = pd.concat(tools, ignore_index=True)

    # Clean names
    final_df["tool_name"] = final_df["tool_name"].replace({
        "deepl": "DeepL",
        "copyai": "Copy.ai",
        "jasperai": "Jasper AI",
        "githubcopilot": "GitHub Copilot"
    })

    return final_df


df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Filters")
tools = df["tool_name"].unique()
selected_tools = st.sidebar.multiselect("Select Tools", tools, default=tools)

filtered_df = df[df["tool_name"].isin(selected_tools)]

# ---------------- TITLE ----------------
st.title("🤖 AI Application Usage Trends")

# ---------------- METRICS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Users", f"{int(filtered_df['users'].sum()):,}")
col2.metric("Total Revenue", f"${filtered_df['revenue'].sum():,.0f}")
col3.metric("Avg Market Share", f"{filtered_df['market_share'].mean():.2f}%")

# ---------------- LINE ----------------
st.subheader("User Growth Over Time")
st.plotly_chart(
    px.line(filtered_df, x="date", y="users", color="tool_name"),
    use_container_width=True
)

# ---------------- BAR ----------------
st.subheader("Revenue Comparison")

bar_df = filtered_df.groupby("tool_name", as_index=False)["revenue"].sum()

st.plotly_chart(
    px.bar(bar_df, x="tool_name", y="revenue", color="tool_name"),
    use_container_width=True
)

# ---------------- PIE ----------------
st.subheader("Market Share")

pie_df = filtered_df.groupby("tool_name", as_index=False)["market_share"].mean()

st.plotly_chart(
    px.pie(pie_df, names="tool_name", values="market_share"),
    use_container_width=True
)

# ---------------- HISTOGRAM ----------------
st.subheader("User Distribution")

st.plotly_chart(
    px.histogram(filtered_df, x="users", nbins=20),
    use_container_width=True
)

# ---------------- SCATTER ----------------
st.subheader("Users vs Revenue")

st.plotly_chart(
    px.scatter(filtered_df, x="users", y="revenue", color="tool_name"),
    use_container_width=True
)

# ---------------- DATA ----------------
st.subheader("Dataset Preview")
st.dataframe(filtered_df.head(50))
