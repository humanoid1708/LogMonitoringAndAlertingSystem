from log_ingestion import read_logs
from alert_engine import error_spike_rule, keyword_spike_rule

logs = read_logs("sample-application.log")

alerts = []
alerts.extend(error_spike_rule(logs, threshold=5, window_minutes=5, label="5 minutes"))
alerts.extend(error_spike_rule(logs, threshold=3, window_minutes=1, label="1 minute"))
alerts.extend(error_spike_rule(logs, threshold=2, window_seconds=10, label="10 seconds"))
alerts.extend(keyword_spike_rule(logs))

print("\n=== ACTIVE ALERTS ===")
if not alerts:
    print("No alerts triggered.")
else:
    for a in alerts:
        print(f"""
ALERT: {a['alert_name']}
Severity: {a['severity']}
Reason: {a['reason']}
Window: {a['window']}
""")