from datetime import datetime, timezone


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def to_date_isoformat(dt):
    return dt.strftime("%Y-%m-%d%:z")
