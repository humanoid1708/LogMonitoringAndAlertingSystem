

def classify_severity(score):
    """
    Classify anomaly severity based on anomaly score
    """
    if score > 3.0:
        return "CRITICAL"
    elif score > 1.5:
        return "MEDIUM"
    else:
        return "LOW"