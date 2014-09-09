import pytz
from datetime import datetime


timezone = pytz.utc


def from_db(timestamp):
    """Convert a timestamp from db to datetime

    This converts a timestamp integer to a timezone-aware
    datetime instance. The timezone is UTC.

    :type timestamp: int or str
    :param timestamp: The timestamp to convert
    :rtype: datetime
    :return: The converted datetime in UTC
    """
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone)


def to_db(time):
    """Convert a datetime instance to a db timestamp

    :type time: datetime
    :param time: The datetime to convert
    :rtype: int
    :return: The unix timestamp for the database
    """
    return int(time.timestamp())


def new_datetime(year, month=None, day=None,
                 hour=0, minute=0, second=0,
                 microsecond=0):
    """Create a new datetime instance with UTC timezone.

    :type year: int
    :type month: int
    :type day: int
    :type hour: int
    :type minute: int
    :type second: int
    :type microsecond: int
    :rtype: datetime
    :return: The datetime instance
    """
    return datetime(year, month, day, hour, minute,
                    second, microsecond, tzinfo=timezone)


def now_datetime():
    """Create a new datetime instance for "NOW"

    :rtype: datetime
    :return: Teh datetime instance
    """
    return datetime.utcnow().replace(tzinfo=timezone)