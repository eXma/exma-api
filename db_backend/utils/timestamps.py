import pytz
from datetime import datetime


def from_db(timestamp):
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).replace(pytz.utc)


def to_db(time):
    return int(time.timestamp())