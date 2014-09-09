import pytz
from datetime import datetime


timezone = pytz.utc


def from_db(timestamp):
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).replace(timezone)


def to_db(time):
    return int(time.timestamp())


def new_datetime(year, month=None, day=None,
                 hour=0, minute=0, second=0,
                 microsecond=0):
    return datetime(year, month, day, hour, minute,
                    second, microsecond, tzinfo=timezone)

def now_datetime():
    return datetime.utcnow().replace(tzinfo=timezone)