from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

st_autorefresh(interval=60000, key="refresh")

# PAGE CONFIG
st.set_page_config(
    page_title="Lead Analytics",
    page_icon="📊",
    layout="wide"
)


# LOAD DATA
data = pd.read_csv("tired - Sheet1.csv")
data.columns = data.columns.str.strip()

# SIDEBAR MENU
with st.sidebar:

    selected = option_menu(
        menu_title="Dashboard",
        options=["Overview", "Analytics", "Leads"],
        icons=["bar-chart", "pie-chart", "table"],
        default_index=0,
    )

# -------- OVERVIEW PAGE -------- #

if selected == "Overview":

    st.title("📊 Lead Generation Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Leads", len(data))
    col2.metric("Unique Companies", data["Company"].nunique())
    col3.metric("Unique Services", data["Service requested"].nunique())
    col4.metric("Phone Numbers", data["Phone number"].nunique())

    st.divider()

    col1, col2 = st.columns(2)

    service_counts = data["Service requested"].value_counts().reset_index()
    service_counts.columns = ["Service", "Count"]

    fig_services = px.bar(
        service_counts,
        x="Service",
        y="Count",
        text="Count",
        color="Service",
        title="Service Demand"
    )

    col1.plotly_chart(fig_services, use_container_width=True)

    budget_counts = data["Budget range"].value_counts().reset_index()
    budget_counts.columns = ["Budget", "Count"]

    fig_budget = px.pie(
        budget_counts,
        names="Budget",
        values="Count",
        hole=0.5,
        title="Budget Distribution"
    )

    col2.plotly_chart(fig_budget, use_container_width=True)

# -------- ANALYTICS PAGE -------- #

elif selected == "Analytics":

    st.title("📈 Lead Analytics")

    if "Date" in data.columns:

        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")

        leads_trend = data.groupby("Date").size().reset_index(name="Leads")

        fig_trend = px.line(
            leads_trend,
            x="Date",
            y="Leads",
            markers=True,
            title="Lead Growth Over Time"
        )

        st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    timeline = data["Timeline"].value_counts().reset_index()
    timeline.columns = ["Timeline", "Count"]

    fig_timeline = px.bar(
        timeline,
        x="Timeline",
        y="Count",
        text="Count",
        color="Timeline",
        title="Project Timeline Demand"
    )

    st.plotly_chart(fig_timeline, use_container_width=True)

# -------- LEADS PAGE -------- #

elif selected == "Leads":

    st.title("📋 Leads Database")

    search = st.text_input("Search Company")

    if search:
        filtered = data[data["Company"].str.contains(search, case=False)]
    else:
        filtered = data

    st.dataframe(filtered, use_container_width=True)