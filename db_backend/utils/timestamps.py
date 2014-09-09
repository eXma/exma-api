import pytz
from datetime import datetime


timezone = pytz.utc


def from_db(timestamp):
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).replace(timezone)


def to_db(time):
    return int(time.timestamp())