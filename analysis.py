import streamlit as st
import pandas as pd
import altair as alt
from log_ingestion import read_logs
from alert_engine import error_spike_rule, keyword_spike_rule

# ---------------- Page Config ----------------
st.set_page_config(page_title="Log Monitoring System", layout="wide")

# ---------------- Global Styles ----------------
st.markdown(
    """
    <style>
    body, .stApp {
        background-color: #020617;
        color: #e5e7eb;
        font-size: 16px;
    }

    .metric-card {
        background: #020617;
        padding: 1.2rem 1.4rem;
        border-radius: 0.75rem;
        border: 1px solid #111827;
        box-shadow: 0 10px 25px rgba(15,23,42,0.7);
    }

    .metric-label {
        font-size: 1rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    .metric-errors { color: #f97373; }
    .metric-warn { color: #facc15; }
    .metric-info { color: #22c55e; }
    .metric-total { color: #38bdf8; }
    .metric-alerts { color: #f97373; }

    .alert-card {
        background: linear-gradient(135deg, rgba(248,113,113,0.15), rgba(127,29,29,0.5));
        border-radius: 0.75rem;
        padding: 1rem 1.25rem;
        border: 1px solid rgba(248,113,113,0.5);
        margin-bottom: 0.75rem;
        font-size: 1rem;
    }

    /* Tab labels */
    div[data-baseweb="tab-list"] button p {
        font-size: 1rem !important;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;">
      <div>
        <div style="font-size:2rem;font-weight:700;color:#e5e7eb;">LogWatch</div>
        <div style="font-size:1.05rem;color:#9ca3af;">Real-time Log Monitoring &amp; Alerting</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- Load Logs ----------------
LOG_FILE = "sample-application.log"   # or logs.json
logs = read_logs(LOG_FILE)
df = pd.DataFrame(logs)

# ---- Safety ----
for col in ["timestamp", "level", "service", "message"]:
    if col not in df.columns:
        df[col] = "unknown"

df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---------------- Alerts (GLOBAL) ----------------
alerts = []
# 5-minute, 1-minute, and 10-second error spikes
alerts.extend(error_spike_rule(logs, threshold=5, window_minutes=5, label="5 minutes"))
alerts.extend(error_spike_rule(logs, threshold=3, window_minutes=1, label="1 minute"))
alerts.extend(error_spike_rule(logs, threshold=2, window_seconds=10, label="10 seconds"))

# Keyword spike (default 5-minute)
alerts.extend(keyword_spike_rule(logs))

# ---------------- Session State ----------------
if "applied_filters" not in st.session_state:
    st.session_state.applied_filters = {
        "level": "ALL",
        "service": "ALL",
        "start_dt": df["timestamp"].min(),
        "end_dt": df["timestamp"].max(),
        "keyword": "",
        "applied": False
    }

# ---------------- Tabs ----------------
tab1, tab2, tab3 = st.tabs(
    ["📊 Dashboard", "🔍 Filter Logs", "🚨 Alerts"]
)

# ================= DASHBOARD =================
with tab1:
    st.subheader("📊 System Overview")

    total_logs = len(df)
    error_logs = len(df[df["level"] == "ERROR"])
    warn_logs = len(df[df["level"] == "WARN"])
    info_logs = len(df[df["level"] == "INFO"])
    services = df["service"].nunique()
    active_alerts = len(alerts)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Total Logs</div>
              <div class="metric-value metric-total">{total_logs}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Errors</div>
              <div class="metric-value metric-errors">{error_logs}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Warnings</div>
              <div class="metric-value metric-warn">{warn_logs}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Infos</div>
              <div class="metric-value metric-info">{info_logs}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Active Alerts</div>
              <div class="metric-value metric-alerts">{active_alerts}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("📈 Log Volume Over Time")
    if not df.empty:
        temp = df.copy()
        temp["minute"] = temp["timestamp"].dt.floor("T")
        counts = (
            temp.groupby(["minute", "level"])
            .size()
            .reset_index(name="count")
        )

        level_order = ["ERROR", "WARN", "INFO"]
        color_scale = alt.Scale(
            domain=level_order,
            range=["#f97373", "#facc15", "#22c55e"],
        )

        chart = (
            alt.Chart(counts)
            .mark_line(point=False, interpolate="monotone")
            .encode(
                x=alt.X("minute:T", title="Time"),
                y=alt.Y("count:Q", title="Log Count"),
                color=alt.Color("level:N", scale=color_scale, title="Level"),
                tooltip=["minute:T", "level:N", "count:Q"],
            )
            .properties(height=260)
        )

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No logs loaded to display trends.")

# ================= FILTER TAB =================
with tab2:
    st.subheader("🔍 Filter Logs")

    af = st.session_state.applied_filters

    # ---- Draft Inputs (NO AUTO APPLY) ----
    level_input = st.selectbox(
        "Log Level",
        ["ALL", "INFO", "WARN", "ERROR"],
        index=["ALL", "INFO", "WARN", "ERROR"].index(af["level"])
    )

    service_list = ["ALL"] + sorted(df["service"].unique())
    service_input = st.selectbox(
        "Service",
        service_list,
        index=service_list.index(af["service"])
    )

    st.subheader("⏱ Date & Time Range")
    start_dt_input = st.datetime_input(
        "Start Date & Time",
        value=af["start_dt"]
    )
    end_dt_input = st.datetime_input(
        "End Date & Time",
        value=af["end_dt"]
    )

    keyword_input = st.text_input(
        "🔎 Keyword Search",
        value=af["keyword"]
    )

    # ---- Centered Buttons ----
    left, center, right = st.columns([3, 4, 3])
    with center:
        b1, gap, b2 = st.columns([1, 0.3, 1])

        with b1:
            if st.button("Apply Filter", use_container_width=True):
                st.session_state.applied_filters = {
                    "level": level_input,
                    "service": service_input,
                    "start_dt": start_dt_input,
                    "end_dt": end_dt_input,
                    "keyword": keyword_input,
                    "applied": True
                }
                st.rerun()

        with b2:
            if st.button("Reset Filter", use_container_width=True):
                st.session_state.applied_filters = {
                    "level": "ALL",
                    "service": "ALL",
                    "start_dt": df["timestamp"].min(),
                    "end_dt": df["timestamp"].max(),
                    "keyword": "",
                    "applied": False
                }
                st.rerun()

    # ---- Show Filtered Logs ONLY if Applied ----
    if st.session_state.applied_filters["applied"]:
        af = st.session_state.applied_filters
        filtered = df.copy()

        if af["level"] != "ALL":
            filtered = filtered[filtered["level"] == af["level"]]

        if af["service"] != "ALL":
            filtered = filtered[filtered["service"] == af["service"]]

        filtered = filtered[
            (filtered["timestamp"] >= af["start_dt"]) &
            (filtered["timestamp"] <= af["end_dt"])
        ]

        if af["keyword"]:
            filtered = filtered[
                filtered["message"].str.contains(
                    af["keyword"], case=False, na=False
                )
            ]

        st.info(f"{len(filtered)} matching logs found")
        st.dataframe(filtered, use_container_width=True)

        st.subheader("⬇ Export Filtered Logs")
        csv_bytes = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name="filtered_logs.csv",
            mime="text/csv",
        )
    else:
        st.warning("No filter applied yet")

# ================= ALERTS =================
with tab3:
    st.subheader("🚨 Active Alerts")
    if alerts:
        for alert in alerts:
            st.error(
                f"""
**{alert['alert_name']}**  
Severity: {alert['severity']}  
Reason: {alert['reason']}  
Threshold: {alert['threshold']}  
Window: {alert['window']}
"""
            )
    else:
        st.success("✅ No active alerts")