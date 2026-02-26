# ml_anomaly.py
from sklearn.ensemble import IsolationForest

def train_iforest(df):
    X = df[["error_count", "log_count", "avg_response_time"]]
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    model.fit(X)
    return model

def predict_iforest(model, df):
    X = df[["error_count", "log_count", "avg_response_time"]]
    df["ml_anomaly_score"] = -model.decision_function(X)
    df["ml_anomaly"] = model.predict(X) == -1
    return df