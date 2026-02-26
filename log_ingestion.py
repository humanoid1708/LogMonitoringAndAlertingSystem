import json
import re
from datetime import datetime

SPRING_LOG_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+'
    r'(?P<level>INFO|WARN|ERROR|DEBUG)\s+'
    r'\d+\s+---\s+\[.*?\]\s+'
    r'(?P<service>[\w\.]+)\s+:\s+'
    r'(?P<message>.*)'
)

import json
import re
from datetime import datetime


def _parse_timestamp(value):
    """
    Support:
    - ISO strings with or without 'Z', e.g. '2026-02-19T10:15:30Z'
    - ISO strings without timezone
    - Epoch seconds as int / float
    """
    # Epoch seconds
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)

    ts_str = str(value)
    # Handle trailing Z (UTC) commonly used in JSON logs
    if ts_str.endswith("Z"):
        ts_str = ts_str.replace("Z", "+00:00")

    return datetime.fromisoformat(ts_str)


def read_logs(filename):
    logs = []

    # -------- JSON FILE (array) --------
    if filename.endswith(".json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for log in data:
                logs.append({
                    "timestamp": _parse_timestamp(log["timestamp"]),
                    "level": log["level"],
                    "service": log.get("service") or log.get("service_name") or log.get("component"),
                    "message": log["message"],
                    "response_time": log.get("response_time", 0)
                })
        return logs

    # -------- TEXT / LOG FILE --------
    pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s+'
        r'(?P<level>INFO|WARN|ERROR|DEBUG)\s+'
        r'\d+\s+---\s+\[.*?\]\s+'
        r'(?P<service>[\w\.]+)\s+:\s+'
        r'(?P<message>.*)'
    )

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if not match:
                continue

            message = match.group("message")
            duration = re.search(r'duration=(\d+)ms', message)

            logs.append({
                "timestamp": datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S.%f"),
                "level": match.group("level"),
                "service": match.group("service"),
                "message": message,
                "response_time": int(duration.group(1)) if duration else 0
            })

    return logs


def parse_json_log(log):
    return {
        "timestamp": datetime.fromisoformat(log["timestamp"]),
        "level": log["level"],
        "service": log["service"],
        "message": log["message"],
        "response_time": log.get("response_time", 0)
    }


def parse_spring_log(match):
    message = match.group("message")
    duration_match = re.search(r'duration=(\d+)ms', message)

    return {
        "timestamp": datetime.strptime(
            match.group("timestamp"),
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        "level": match.group("level"),
        "service": match.group("service"),
        "message": message,
        "response_time": int(duration_match.group(1)) if duration_match else 0
    }