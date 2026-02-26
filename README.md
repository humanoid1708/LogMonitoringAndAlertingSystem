# Log Monitoring and Alerting System

## Project Overview
This project implements a log monitoring and alerting system that ingests application logs, analyzes them, and presents insights through an interactive dashboard. The system supports multiple log formats, rule-based alerting, advanced filtering, and export of results for further analysis.

---

## Design Decisions

### Modular Architecture
The system is designed with clear separation of concerns:
- *Log ingestion* handles parsing and normalization of logs
- *Alert engine* encapsulates rule-based alert logic
- *UI layer* manages visualization, filtering, and user interaction

This improves maintainability and allows easy extension of alert rules or input formats.

---

### Tab-Based User Interface
The UI is organized into separate tabs to keep functionality clear and uncluttered:

- *Dashboard*: High-level metrics and error trends
- *Alerts*: Active alerts with severity and explanation
- *Filter Logs*: User-controlled filtering with apply/reset actions
- *Logs*: Complete, unfiltered log view
- *Export*: Download filtered logs as CSV

---

### Controlled Filtering
Filters are applied only when the user clicks *Apply Filter*:
- Prevents automatic refresh on every input change
- Improves clarity and predictability
- *Reset Filter* clears inputs and removes filtered results from view

---

### Log Format Normalization
The system supports both structured and unstructured logs:
- .json
- .log / .txt

All logs are normalized into a common schema:
timestamp | level | service | message | response_time
This ensures consistent filtering and alert evaluation across formats.

---

## Alert Rules Implemented

### High Error Rate Alert
- Triggered when the number of ERROR logs exceeds a defined threshold within a time window
- Severity: *HIGH*
- Purpose: Detects critical system failures or instability

---

### Keyword Spike Alert
- Triggered when a critical keyword (e.g., timeout, failed, exception) appears frequently in log messages
- Severity: *MEDIUM*
- Purpose: Identifies recurring failure patterns not always classified as errors

---

### Severity Levels
- *HIGH*: Critical issue requiring immediate attention
- *MEDIUM*: Warning condition requiring investigation
- *LOW*: Informational (extensible if required)

Severity is assigned within the alert rule logic and displayed with each alert.

---

## How to Run the Project

### Prerequisites
- Python 3.8 or higher
- pip

### Install Dependencies
```
pip install -r requirements.txt
```
### Run the Application
```
streamlit run analysis.py
```
The application will be available at:
http://localhost:8501
