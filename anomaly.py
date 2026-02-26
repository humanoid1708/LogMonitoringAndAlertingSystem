import numpy as np

def compute_anomaly_score(df):
    """
    Compute anomaly score using magnitude of standardized features
    """
    features = df[["error_count", "log_count", "avg_response_time"]]
    df["anomaly_score"] = np.linalg.norm(features.values, axis=1)
    return df