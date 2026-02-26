# preprocess.py
import re
import pandas as pd
from sklearn.preprocessing import StandardScaler

LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+'
    r'(?P<level>INFO|WARN|ERROR)\s+'
    r'(?P<service>\w+)\s+-\s+(?P<message>.*)'
)

def parse_logs(log_lines):
    records = []
    for line in log_lines:
        match = LOG_PATTERN.search(line)
        if match:
            records.append(match.groupdict())
    return pd.DataFrame(records)

import pandas as pd
from sklearn.preprocessing import StandardScaler

def normalize(logs):
    """
    logs: list[dict] coming from read_logs()
    """

    if not logs or not isinstance(logs, list):
        return None

    df = pd.DataFrame(logs)

    # safety check
    required_cols = {"timestamp", "level", "service"}
    if not required_cols.issubset(df.columns):
        return None

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["error_flag"] = (df["level"] == "ERROR").astype(int)

    agg = df.groupby(
        [pd.Grouper(key="timestamp", freq="1min"), "service"]
    ).agg(
        error_count=("error_flag", "sum"),
        log_count=("level", "count"),
        avg_response_time=("response_time", "mean")
    ).reset_index()

    scaler = StandardScaler()
    agg[["error_count", "log_count", "avg_response_time"]] = scaler.fit_transform(
        agg[["error_count", "log_count", "avg_response_time"]]
    )

    return agg