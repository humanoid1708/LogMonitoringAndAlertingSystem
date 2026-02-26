def filter_by_level(logs, level):
    return [l for l in logs if l["level"] == level]

def filter_by_service(logs, service):
    return [l for l in logs if l["service"] == service]

def filter_by_time_range(logs, start, end):
    return [l for l in logs if start <= l["timestamp"] <= end]

def filter_by_keyword(logs, keyword):
    return [l for l in logs if keyword.lower() in l["message"].lower()]