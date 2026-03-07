from streamlit_autorefresh import st_autorefresh
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import requests
from datetime import datetime

# ── AUTO REFRESH EVERY 10 SECONDS ──────────────────────────────────────────
st_autorefresh(interval=10000, key="refresh")

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GrowthPath Lead Analytics",
    page_icon="📊",
    layout="wide"
)

# ── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .last-updated {
        font-size: 12px;
        color: #64748b;
        text-align: right;
        margin-bottom: 10px;
    }
    .latest-lead-hot {
        background: linear-gradient(135deg, #1a0a0a, #2d0f0f);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .latest-lead-warm {
        background: linear-gradient(135deg, #1a140a, #2d1f0a);
        border: 1px solid #f59e0b;
        border-left: 5px solid #f59e0b;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .latest-lead-cold {
        background: linear-gradient(135deg, #0a0f1a, #0a182d);
        border: 1px solid #60a5fa;
        border-left: 5px solid #60a5fa;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .lead-card-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
    .lead-card-detail { font-size: 13px; color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA FROM SUPABASE ──────────────────────────────────────────────────
@st.cache_data(ttl=60)
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
            df.columns = df.columns.str.strip()
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            # Normalise lead_score to uppercase single word
            if "lead_score" in df.columns:
                df["lead_score"] = df["lead_score"].astype(str).str.strip().str.split().str[0].str.upper()
            # Normalise status
            if "status" in df.columns:
                df["status"] = df["status"].astype(str).str.strip()
            return df
        else:
            st.error(f"Supabase error {response.status_code}: {response.text}")
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

data = load_data()

# ── LAST UPDATED ─────────────────────────────────────────────────────────────
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

    st.markdown('<small style="color:#475569;">Auto-refreshes every 60s</small>', unsafe_allow_html=True)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if data.empty:
    st.warning("⚠️ No data found. Check your Supabase connection in secrets.")
    st.stop()

# ── HELPER: safe column getter ────────────────────────────────────────────────
def col(df, *names):
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

# ── SHARED METRICS ────────────────────────────────────────────────────────────
total  = len(data)
hot    = len(data[data[SCORE_COL].str.upper() == "HOT"]) if SCORE_COL else 0
warm   = len(data[data[SCORE_COL].str.upper() == "WARM"]) if SCORE_COL else 0
cold   = len(data[data[SCORE_COL].str.upper() == "COLD"]) if SCORE_COL else 0
# Fix: match both "Meeting Booked" and "Meetings Booked"
booked = len(data[data[STATUS_COL].str.lower().str.contains("meeting booked", na=False)]) if STATUS_COL else 0
conversion = round((booked / total * 100), 1) if total > 0 else 0

COLOR_MAP = {"HOT": "#ef4444", "WARM": "#f59e0b", "COLD": "#60a5fa"}

# ════════════════════════════════════════════════════════════════════════════
# OVERVIEW PAGE
# ════════════════════════════════════════════════════════════════════════════
if selected == "Overview":

    st.title("📊 Lead Generation Overview")

    # KPI METRICS — 6 columns
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🧑‍💼 Total Leads", total)
    c2.metric("🔥 Hot Leads", hot)
    c3.metric("🌤 Warm Leads", warm)
    c4.metric("❄️ Cold Leads", cold)
    c5.metric("📅 Meetings Booked", booked)
    c6.metric("📈 Conversion Rate", f"{conversion}%")

    st.divider()

    # LATEST LEAD CARD
    if not data.empty and NAME_COL and SCORE_COL:
        latest = data.iloc[0]
        score_val = str(latest.get(SCORE_COL, "")).upper()
        card_class = "latest-lead-hot" if score_val == "HOT" else "latest-lead-warm" if score_val == "WARM" else "latest-lead-cold"
        score_emoji = "🔥" if score_val == "HOT" else "🌤" if score_val == "WARM" else "❄️"
        st.markdown(f"""
        <div class="{card_class}">
            <div class="lead-card-title">{score_emoji} Latest Lead — {latest.get(NAME_COL, 'Unknown')}</div>
            <div class="lead-card-detail">
                📧 {latest.get(EMAIL_COL, 'N/A')} &nbsp;|&nbsp;
                📞 {latest.get(PHONE_COL, 'N/A')} &nbsp;|&nbsp;
                🏢 {latest.get(COMPANY_COL, 'N/A')} &nbsp;|&nbsp;
                🎯 Score: <strong>{score_val}</strong> &nbsp;|&nbsp;
                📌 Status: <strong>{latest.get(STATUS_COL, 'N/A')}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # CHARTS ROW
    c1, c2, c3 = st.columns(3)

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
        def clean_budget(label):
            label = str(label)
            if "Less" in label or ("500" in label and "2,000" not in label): return "Below ₦500k"
            if "500" in label and "2,000" in label: return "₦500k – ₦2M"
            if "2,000" in label or "2M" in label: return "Above ₦2M"
            return label.split("(")[0].strip()
        budget_counts["Budget"] = budget_counts["Budget"].apply(clean_budget)
        fig_budget = px.pie(
            budget_counts, names="Budget", values="Count",
            hole=0.5, title="💰 Budget Distribution",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_budget.update_traces(textposition="inside", textinfo="percent+label")
        c2.plotly_chart(fig_budget, use_container_width=True)

    # LEAD SCORE DONUT on Overview
    if SCORE_COL:
        score_counts = data[SCORE_COL].value_counts().reset_index()
        score_counts.columns = ["Score", "Count"]
        fig_donut = px.pie(
            score_counts, names="Score", values="Count",
            hole=0.6, title="🎯 Lead Score Split",
            color="Score", color_discrete_map=COLOR_MAP
        )
        c3.plotly_chart(fig_donut, use_container_width=True)

    # LEAD TREND SPARKLINE
    if DATE_COL:
        leads_trend = data.groupby(data[DATE_COL].dt.date).size().reset_index(name="Leads")
        leads_trend.columns = ["Date", "Leads"]
        leads_trend["Date"] = pd.to_datetime(leads_trend["Date"])
        fig_trend = px.line(
            leads_trend, x="Date", y="Leads",
            markers=True, title="📅 Lead Growth Over Time",
            color_discrete_sequence=["#6366f1"]
        )
        fig_trend.update_traces(fill="tozeroy", fillcolor="rgba(99,102,241,0.1)")
        fig_trend.update_xaxes(tickformat="%d %b %Y", tickangle=-30)
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Number of Leads")
        st.plotly_chart(fig_trend, use_container_width=True)

    # LATEST 5 LEADS TABLE
    st.subheader("🆕 Latest 5 Leads")
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
        leads_trend["Date"] = pd.to_datetime(leads_trend["Date"])
        fig_trend = px.line(
            leads_trend, x="Date", y="Leads",
            markers=True, title="📅 Lead Growth Over Time",
            color_discrete_sequence=["#6366f1"]
        )
        fig_trend.update_traces(fill="tozeroy", fillcolor="rgba(99,102,241,0.1)")
        fig_trend.update_xaxes(tickformat="%d %b %Y", tickangle=-30)
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Number of Leads")
        st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    c1, c2 = st.columns(2)

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

    if STATUS_COL:
        status_counts = data[STATUS_COL].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(
            status_counts, names="Status", values="Count",
            title="📋 Lead Status Breakdown",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        c2.plotly_chart(fig_status, use_container_width=True)

    # CONVERSION FUNNEL
    st.divider()
    st.subheader("🔽 Lead Conversion Funnel")
    funnel_data = pd.DataFrame({
        "Stage": ["Total Leads", "Hot Leads", "Meetings Booked"],
        "Count": [total, hot, booked]
    })
    fig_funnel = px.funnel(funnel_data, x="Count", y="Stage",
                           color_discrete_sequence=["#6366f1", "#ef4444", "#22c55e"])
    st.plotly_chart(fig_funnel, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# LEADS PAGE
# ════════════════════════════════════════════════════════════════════════════
elif selected == "Leads":

    st.title("📋 Leads Database")

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

    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🔥 Hot", hot)
    m2.metric("🌤 Warm", warm)
    m3.metric("❄️ Cold", cold)
    m4.metric("📈 Conversion", f"{conversion}%")

    st.divider()

    c1, c2 = st.columns(2)

    score_counts = data[SCORE_COL].value_counts().reset_index()
    score_counts.columns = ["Score", "Count"]

    fig_score = px.bar(
        score_counts, x="Score", y="Count",
        text="Count", color="Score",
        title="Lead Score Distribution",
        color_discrete_map=COLOR_MAP
    )
    c1.plotly_chart(fig_score, use_container_width=True)

    fig_donut = px.pie(
        score_counts, names="Score", values="Count",
        hole=0.6, title="Score Share",
        color="Score", color_discrete_map=COLOR_MAP
    )
    c2.plotly_chart(fig_donut, use_container_width=True)

    st.divider()
    st.subheader("🔥 Hot Leads — Priority Follow Up")
    hot_leads = data[data[SCORE_COL].str.upper() == "HOT"]
    display_cols = [c for c in [NAME_COL, EMAIL_COL, PHONE_COL, COMPANY_COL, BUDGET_COL, STATUS_COL, DATE_COL] if c]
    if not hot_leads.empty:
        st.dataframe(hot_leads[display_cols], use_container_width=True)
    else:
        st.info("No hot leads yet.")

