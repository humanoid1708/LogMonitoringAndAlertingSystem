# LogWatch – ML & DL Log Monitoring System

## Project Overview

LogWatch is an intelligent log analysis and monitoring dashboard designed to ingest application logs, detect anomalies using Machine Learning (ML) and Deep Learning (DL), and provide real-time alerting based on predefined heuristics and anomaly detection models.

The system combines rule-based monitoring with AI-driven anomaly detection to ensure robust and scalable log monitoring.

---

# Design Decisions

## 1. Modular Pipeline Architecture

The system follows a modular architecture to ensure scalability and separation of concerns:

- **Ingestion & Normalization Layer**
  - Parses raw logs
  - Converts logs into structured DataFrames
  - Encodes categorical features for ML models

- **Hybrid Detection Engine**
  - **Heuristic Layer**: Fast rule-based detection for known patterns
  - **ML Layer (Isolation Forest)**: Unsupervised anomaly detection for unusual log frequency or distribution
  - **DL Layer (LSTM Autoencoder)**: Sequence-based anomaly detection to capture temporal irregularities

- **Root Cause Analysis Layer**
  - Correlates anomaly scores with services and timestamps
  - Helps identify the source of failures

---

## 2. Hybrid Detection Strategy

### Heuristic Alerts
Used for known error patterns such as error spikes and keyword bursts.

### Machine Learning (Isolation Forest)
Detects logs that statistically deviate from the baseline behavior.

### Deep Learning (LSTM Autoencoder)
Reconstructs log sequences and flags anomalies when reconstruction error exceeds threshold.

This layered design ensures:
- Fast detection for known issues
- Adaptive detection for unknown patterns
- Temporal anomaly recognition

---

## 3. Thematic User Interface

The system uses a tab-based Streamlit dashboard with:

- Dashboard
- AI Monitoring
- Filter
- Alerts

This prevents information overload and improves usability.

---

# Alert Rules Implemented

## 1. Rule-Based Alerts (Heuristics)

### Error Spike Rule
Monitors the number of `ERROR` logs within a defined time window.
- Triggers when count exceeds threshold
- Severity: HIGH

### Keyword Spike Rule
Scans log messages for critical keywords such as:
- "Critical"
- "Timeout"
- "Database Down"

Triggers alert when keyword frequency increases sharply.

---

## 2. AI-Driven Alerts (Anomalies)

### Isolation Forest (ML)
Identifies statistically abnormal logs compared to baseline distribution.

### LSTM Autoencoder (DL)
Detects anomalies in log sequences based on reconstruction error.

---

# Project Structure
app.py # Main Streamlit entry point
log_ingestion.py # Log reading and initial parsing
preprocess.py # Feature engineering & normalization
ml_anomaly.py # Isolation Forest model
dl_lstm.py # LSTM Autoencoder model
alert_engine.py # Heuristic spike rules
sample_application.log # Sample log file
requirements.txt

---

# How to Run the Project

## 1. Prerequisites

Ensure you have:

- Python 3.8+
- pip

Required Libraries:
- Streamlit
- Pandas
- Altair
- PyTorch
- Scikit-learn

---

## 2. Installation

Clone the repository and install dependencies:
`pip install -r requirements.txt`

## 3. Execution

Place your log file (e.g., `sample_application.log`) in the root directory.

`streamlit run app.py`
