# root_cause.py

def find_root_cause(df, threshold=2.5):
    anomalous = df[df["anomaly_score"] > threshold]

    if anomalous.empty:
        return None

    first = anomalous.sort_values("timestamp").iloc[0]
    return {
        "service": first["service"],
        "timestamp": first["timestamp"],
        "score": round(first["anomaly_score"], 2)
    }