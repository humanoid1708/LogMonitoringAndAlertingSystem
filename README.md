## Log Monitoring & Alerting System

### Features
- Log ingestion from JSON file
- Search and filter by level and service
- Rule-based alert engine
- Clear alert explanations
- Error trend visualization
- CSV export of filtered logs

### Alert Rules
1. ERROR count exceeds threshold within a time window
2. Keyword spike detection (e.g., "timeout")

### How to Run
pip install -r requirements.txt  
streamlit run analysis.py