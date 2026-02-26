from datetime import timedelta

def error_spike_rule(logs, threshold=5, window_minutes=5):
    alerts = []
    if not logs:
        return alerts

    latest = max(l["timestamp"] for l in logs)
    window_start = latest - timedelta(minutes=window_minutes)

    window_logs = [l for l in logs if l["timestamp"] >= window_start]
    error_logs = [l for l in window_logs if l["level"] == "ERROR"]

    if len(error_logs) > threshold:
        alerts.append({
            "alert_name": "High Error Rate",
            "severity": "HIGH",
            "reason": f"{len(error_logs)} ERROR logs in last {window_minutes} minutes",
            "threshold": threshold,
            "window": f"{window_minutes} minutes"
        })

    return alerts


def keyword_spike_rule(logs, keyword="timeout", threshold=3, window_minutes=5):
    alerts = []
    if not logs:
        return alerts

    latest = max(l["timestamp"] for l in logs)
    window_start = latest - timedelta(minutes=window_minutes)

    window_logs = [l for l in logs if l["timestamp"] >= window_start]
    hits = [l for l in window_logs if keyword.lower() in l["message"].lower()]

    if len(hits) > threshold:
        alerts.append({
            "alert_name": "Keyword Spike",
            "severity": "LOW",
            "reason": f"Keyword '{keyword}' occurred {len(hits)} times in {window_minutes} minutes",
            "threshold": threshold,
            "window": f"{window_minutes} minutes"
        })

    return alerts