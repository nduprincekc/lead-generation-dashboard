from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import requests
from datetime import datetime

# ── AUTO REFRESH EVERY 60 SECONDS ──────────────────────────────────────────
st_autorefresh(interval=60000, key="refresh")

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GrowthPath Lead Analytics",
    page_icon="📊",
    layout="wide"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: #1e2535;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #6366f1;
    }
    .hot { color: #ef4444; font-weight: 700; }
    .warm { color: #f59e0b; font-weight: 700; }
    .cold { color: #60a5fa; font-weight: 700; }
    .last-updated {
        font-size: 12px;
        color: #64748b;
        text-align: right;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA FROM SUPABASE ──────────────────────────────────────────────────
@st.cache_data(ttl=60)  # Cache for 60 seconds, then re-fetch
def load_data():
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        TABLE_NAME   = st.secrets.get("TABLE_NAME", "leads")

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}?select=*&order=date.desc",
            headers=headers
        )

        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            if df.empty:
                return pd.DataFrame()
            # Normalise column names
            df.columns = df.columns.str.strip()
            # Parse date
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            return df
        else:
            st.error(f"Supabase error {response.status_code}: {response.text}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

data = load_data()

# ── LAST UPDATED TIMESTAMP ───────────────────────────────────────────────────
st.markdown(
    f'<div class="last-updated">🔄 Last updated: {datetime.now().strftime("%d %b %Y, %H:%M:%S")}</div>',
    unsafe_allow_html=True
)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.markdown("### GrowthPath Digital")
    st.markdown("---")

    selected = option_menu(
        menu_title="Dashboard",
        options=["Overview", "Analytics", "Leads", "Lead Score"],
        icons=["bar-chart", "pie-chart", "table", "fire"],
        default_index=0,
    )

    st.markdown("---")
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        f'<small style="color:#475569;">Auto-refreshes every 60s</small>',
        unsafe_allow_html=True
    )

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if data.empty:
    st.warning("⚠️ No data found. Check your Supabase connection in secrets.")
    st.stop()

# ── HELPER: safe column getter ────────────────────────────────────────────────
def col(df, *names):
    """Return first matching column name (case-insensitive)."""
    for n in names:
        for c in df.columns:
            if c.lower() == n.lower():
                return c
    return None

NAME_COL     = col(data, "lead_name", "name", "lead name")
EMAIL_COL    = col(data, "email")
PHONE_COL    = col(data, "phone_number", "phone")
COMPANY_COL  = col(data, "company")
SERVICE_COL  = col(data, "service_requested", "services", "service requested")
BUDGET_COL   = col(data, "budget_range", "budget")
TIMELINE_COL = col(data, "timeline")
SCORE_COL    = col(data, "lead_score", "score")
STATUS_COL   = col(data, "status")
DATE_COL     = col(data, "date", "created_at")

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW PAGE
# ════════════════════════════════════════════════════════════════════════════
if selected == "Overview":

    st.title("📊 Lead Generation Overview")

    # KPI METRICS
    col1, col2, col3, col4, col5 = st.columns(5)

    total = len(data)
    hot   = len(data[data[SCORE_COL].str.upper().str.contains("HOT", na=False)]) if SCORE_COL else 0
    warm  = len(data[data[SCORE_COL].str.upper().str.contains("WARM", na=False)]) if SCORE_COL else 0
    cold  = len(data[data[SCORE_COL].str.upper().str.contains("COLD", na=False)]) if SCORE_COL else 0
    booked = len(data[data[STATUS_COL].str.upper().str.contains("MEETING BOOKED", na=False)]) if STATUS_COL else 0

    col1.metric("🧑‍💼 Total Leads", total)
    col2.metric("🔥 Hot Leads", hot)
    col3.metric("🌤 Warm Leads", warm)
    col4.metric("❄️ Cold Leads", cold)
    col5.metric("📅 Meetings Booked", booked)

    st.divider()

    # CHARTS ROW 1
    c1, c2 = st.columns(2)

    if SERVICE_COL:
        service_counts = data[SERVICE_COL].value_counts().reset_index()
        service_counts.columns = ["Service", "Count"]
        fig_services = px.bar(
            service_counts, x="Service", y="Count",
            text="Count", color="Service",
            title="📌 Service Demand",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_services.update_layout(showlegend=False)
        c1.plotly_chart(fig_services, use_container_width=True)

    if BUDGET_COL:
        budget_counts = data[BUDGET_COL].value_counts().reset_index()
        budget_counts.columns = ["Budget", "Count"]
        fig_budget = px.pie(
            budget_counts, names="Budget", values="Count",
            hole=0.5, title="💰 Budget Distribution",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        c2.plotly_chart(fig_budget, use_container_width=True)

    # LATEST 5 LEADS
    st.subheader("🆕 Latest Leads")
    display_cols = [c for c in [NAME_COL, EMAIL_COL, PHONE_COL, SCORE_COL, STATUS_COL, DATE_COL] if c]
    st.dataframe(data[display_cols].head(5), use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# ANALYTICS PAGE
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Analytics":

    st.title("📈 Lead Analytics")

    # LEAD TREND OVER TIME
    if DATE_COL:
        leads_trend = data.groupby(data[DATE_COL].dt.date).size().reset_index(name="Leads")
        leads_trend.columns = ["Date", "Leads"]
        fig_trend = px.line(
            leads_trend, x="Date", y="Leads",
            markers=True, title="📅 Lead Growth Over Time",
            color_discrete_sequence=["#6366f1"]
        )
        fig_trend.update_traces(fill="tozeroy", fillcolor="rgba(99,102,241,0.1)")
        st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    c1, c2 = st.columns(2)

    # TIMELINE DEMAND
    if TIMELINE_COL:
        timeline = data[TIMELINE_COL].value_counts().reset_index()
        timeline.columns = ["Timeline", "Count"]
        fig_timeline = px.bar(
            timeline, x="Timeline", y="Count",
            text="Count", color="Timeline",
            title="⏱ Project Timeline Demand",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        c1.plotly_chart(fig_timeline, use_container_width=True)

    # STATUS BREAKDOWN
    if STATUS_COL:
        status_counts = data[STATUS_COL].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(
            status_counts, names="Status", values="Count",
            title="📋 Lead Status Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        c2.plotly_chart(fig_status, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LEADS PAGE
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Leads":

    st.title("📋 Leads Database")

    # FILTERS
    f1, f2, f3 = st.columns(3)

    search = f1.text_input("🔍 Search by Name or Company")

    score_filter = "All"
    if SCORE_COL:
        scores = ["All"] + sorted(data[SCORE_COL].dropna().unique().tolist())
        score_filter = f2.selectbox("🎯 Filter by Lead Score", scores)

    status_filter = "All"
    if STATUS_COL:
        statuses = ["All"] + sorted(data[STATUS_COL].dropna().unique().tolist())
        status_filter = f3.selectbox("📌 Filter by Status", statuses)

    filtered = data.copy()

    if search:
        mask = pd.Series([False] * len(filtered))
        for c in [NAME_COL, COMPANY_COL]:
            if c:
                mask |= filtered[c].astype(str).str.contains(search, case=False, na=False)
        filtered = filtered[mask]

    if score_filter != "All" and SCORE_COL:
        filtered = filtered[filtered[SCORE_COL] == score_filter]

    if status_filter != "All" and STATUS_COL:
        filtered = filtered[filtered[STATUS_COL] == status_filter]

    st.markdown(f"**{len(filtered)} leads found**")
    st.dataframe(filtered, use_container_width=True, height=500)

    # DOWNLOAD
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv, "leads_export.csv", "text/csv")

# ════════════════════════════════════════════════════════════════════════════
# LEAD SCORE PAGE
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Lead Score":

    st.title("🔥 Lead Score Breakdown")

    if not SCORE_COL:
        st.warning("No lead_score column found in your database.")
        st.stop()

    c1, c2 = st.columns(2)

    score_counts = data[SCORE_COL].value_counts().reset_index()
    score_counts.columns = ["Score", "Count"]

    color_map = {"HOT": "#ef4444", "WARM": "#f59e0b", "COLD": "#60a5fa"}
    fig_score = px.bar(
        score_counts, x="Score", y="Count",
        text="Count", color="Score",
        title="Lead Score Distribution",
        color_discrete_map=color_map
    )
    c1.plotly_chart(fig_score, use_container_width=True)

    fig_donut = px.pie(
        score_counts, names="Score", values="Count",
        hole=0.6, title="Score Share",
        color="Score", color_discrete_map=color_map
    )
    c2.plotly_chart(fig_donut, use_container_width=True)

    st.divider()
    st.subheader("🔥 Hot Leads — Priority Follow Up")

    if SCORE_COL:
        hot_leads = data[data[SCORE_COL].str.upper().str.contains("HOT", na=False)]
        display_cols = [c for c in [NAME_COL, EMAIL_COL, PHONE_COL, COMPANY_COL, BUDGET_COL, STATUS_COL, DATE_COL] if c]
        if not hot_leads.empty:
            st.dataframe(hot_leads[display_cols], use_container_width=True)
        else:
            st.info("No hot leads yet.")
