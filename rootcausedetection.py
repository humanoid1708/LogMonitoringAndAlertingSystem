# root_cause.py
import pandas as pd

def detect_root_cause(df, anomaly_scores):
    df['anomaly'] = anomaly_scores
    first = (
        df.sort_values('timestamp')
          .groupby('service')['anomaly']
          .mean()
          .sort_values(ascending=False)
    )
    return first.index[0]