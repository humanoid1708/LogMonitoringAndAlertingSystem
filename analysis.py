import streamlit as st
import pandas as pd
from log_ingestion import read_logs
from alert_engine import error_spike_rule, keyword_spike_rule

# ---------------- Page Config ----------------
st.set_page_config(page_title="Log Monitoring System", layout="wide")
st.title("📊 Log Monitoring & Alerting System")

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
alerts.extend(error_spike_rule(logs))
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Dashboard", "🚨 Alerts", "🔍 Filter Logs", "📂 Logs", "⬇ Export"]
)

# ================= DASHBOARD =================
with tab1:
    st.subheader("📊 System Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Logs", len(df))
        st.metric("Error Logs", len(df[df["level"] == "ERROR"]))
    with col2:
        st.metric("Active Alerts", len(alerts))
        st.metric("Services", df["service"].nunique())

    st.subheader("📈 Error Count Over Time")
    error_df = df[df["level"] == "ERROR"]
    if not error_df.empty:
        st.line_chart(error_df.groupby(error_df["timestamp"].dt.minute).size())
    else:
        st.success("No ERROR logs detected")

# ================= ALERTS =================
with tab2:
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

# ================= FILTER TAB =================
with tab3:
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

# ================= LOGS TAB =================
with tab4:
    st.subheader("📂 All Logs")
    st.dataframe(df, use_container_width=True)

# ================= EXPORT TAB =================
with tab5:
    st.subheader("⬇ Export Logs")
    st.info("Exports ONLY the applied filtered logs")

    if st.button("Export Filtered Logs to CSV"):
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

            filtered.to_csv("filtered_logs.csv", index=False)
            st.success("filtered_logs.csv exported")
        else:
            st.warning("No filter applied yet")