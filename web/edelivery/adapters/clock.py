from datetime import datetime, timezone


def timestamp():
    return datetime.now(timezone.utc).isoformat()
