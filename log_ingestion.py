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

def read_logs(filename):
    logs = []

    # -------- JSON FILE (array) --------
    if filename.endswith(".json"):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            for log in data:
                logs.append({
                    "timestamp": datetime.fromisoformat(log["timestamp"]),
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