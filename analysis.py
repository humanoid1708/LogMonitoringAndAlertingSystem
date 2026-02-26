import streamlit as st
import pandas as pd
import altair as alt
import torch

from log_ingestion import read_logs
from preprocess import normalize
from alert_engine import error_spike_rule, keyword_spike_rule
from anomaly import compute_anomaly_score
from root_cause import find_root_cause

from ml_anomaly import train_iforest, predict_iforest

from dl_lstm import LSTMAutoEncoder
from dl_utils import build_sequences
from dl_anamoly import compute_dl_anomaly


st.set_page_config(page_title="Log Monitoring System", layout="wide")

st.markdown(
    """
    <style>
    body, .stApp { background-color:#020617; color:#e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 LogWatch – ML & DL Log Monitoring")

LOG_FILE = "sample-application.log"
logs = read_logs(LOG_FILE)
df = pd.DataFrame(logs)

for col in ["timestamp", "level", "service", "message"]:
    if col not in df.columns:
        df[col] = "unknown"

df["timestamp"] = pd.to_datetime(df["timestamp"])

alerts = []
alerts.extend(error_spike_rule(logs))
alerts.extend(keyword_spike_rule(logs))

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "🤖 AI Monitoring", "🔍 Filter Logs", "🚨 Alerts"]
)

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Logs", len(df))
    c2.metric("Errors", len(df[df["level"] == "ERROR"]))
    c3.metric("Services", df["service"].nunique())
    c4.metric("Active Alerts", len(alerts))

    temp = df.copy()
    temp["minute"] = temp["timestamp"].dt.floor("T")
    counts = temp.groupby(["minute", "level"]).size().reset_index(name="count")

    chart = (
        alt.Chart(counts)
        .mark_line()
        .encode(
            x="minute:T",
            y="count:Q",
            color="level:N",
            tooltip=["minute:T", "level:N", "count:Q"],
        )
    )
    st.altair_chart(chart, use_container_width=True)

with tab2:
    st.subheader("🤖 AI Monitoring (ML + DL)")

    features = normalize(logs)

    if features is None or features.empty:
        st.warning("Not enough data for AI analysis")
    else:
        features = compute_anomaly_score(features)

        st.subheader("📊 Baseline Anomaly Scores")
        st.dataframe(features, use_container_width=True)

        model_ml = train_iforest(features)
        features = predict_iforest(model_ml, features)

        st.subheader("🧠 ML Anomalies (Isolation Forest)")
        st.dataframe(
            features[features["ml_anomaly"] == True],
            use_container_width=True
        )

        seqs = build_sequences(features)

        if len(seqs) > 5:
            model_dl = LSTMAutoEncoder(input_size=3)
            dl_scores = compute_dl_anomaly(model_dl, seqs)

            features = features.iloc[len(features) - len(dl_scores):].copy()
            features["dl_anomaly_score"] = dl_scores

            st.subheader("🧠 DL Anomalies (LSTM Autoencoder)")
            st.dataframe(
                features.sort_values("dl_anomaly_score", ascending=False).head(10),
                use_container_width=True
            )

        root = find_root_cause(features)

        if root:
            st.error(
                f"""
🔥 ROOT CAUSE DETECTED  
Service: {root['service']}  
Time: {root['timestamp']}  
Score: {root['score']}
"""
            )
        else:
            st.success("No root cause detected")

with tab3:
    level = st.selectbox("Level", ["ALL", "INFO", "WARN", "ERROR"])
    service = st.selectbox("Service", ["ALL"] + sorted(df["service"].unique()))
    keyword = st.text_input("Keyword")

    filtered = df.copy()
    if level != "ALL":
        filtered = filtered[filtered["level"] == level]
    if service != "ALL":
        filtered = filtered[filtered["service"] == service]
    if keyword:
        filtered = filtered[filtered["message"].str.contains(keyword, case=False)]

    st.dataframe(filtered, use_container_width=True)
    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False),
        "filtered_logs.csv",
        "text/csv"
    )

with tab4:
    if alerts:
        for a in alerts:
            st.error(
                f"""
**{a['alert_name']}**  
Severity: {a['severity']}  
Reason: {a['reason']}  
Window: {a['window']}
"""
            )
    else:
        st.success("No active alerts")