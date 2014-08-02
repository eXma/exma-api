from datetime import timedelta, datetime, date, time

from dateutil.relativedelta import relativedelta
from db_backend.utils.events import EventCategory
from flask.ext.restful import reqparse, abort
from functools import wraps


class EventInterval():
    """This represents a event date interval.

    It can be parsed from the current request. The start and
    end date in the request is optional and can be computed.

    If start and end is not given, then the begin of the month
    from "today" will be the start date.
    If end but not start is given, then the start date will
    be 1 month and one day before the given end date.
    If the end date is not given it will be one month and one
    day after the start (computed or given).
    """
    max_interval = timedelta(days=100)

    def __init__(self):
        self._start = None
        self._end = None

    def _parse(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start', type=int)
        parser.add_argument('end', type=int)
        req_args = parser.parse_args()

        if req_args.get("start") is not None:
            start = datetime.fromtimestamp(req_args.get("start"))
        else:
            start = None

        if req_args.get("end") is not None:
            end = datetime.fromtimestamp(req_args.get("end"))
        else:
            end = None

        if start is None:
            if end is None:
                start = datetime.combine(date.today() + relativedelta(day=1),
                                         time())
            else:
                start = datetime.combine(end.date() - relativedelta(day=1, months=+1),
                                         time())

        if end is None:
            end = datetime.combine(start.date() + relativedelta(months=+1),
                                   time())

        if end < start:
            abort(400, message="start cannot be before end!")

        if end - start > self.max_interval:
            abort(400, message="time interval too wide")

        self._start = start
        self._end = end

    @property
    def start(self):
        """Get the start date of the interval

        :rtype: datetime
        :return: The start date.
        """
        if self._start is None:
            self._parse()
        return self._start

    @property
    def end(self):
        """get the end date of the interval

        :rtype: datetime
        :return: The end date.
        """
        if self._end is None:
            self._parse()
        return self._end


def _resolve_category(fn):
    @wraps(fn)
    def nufun(*args, **kwargs):
        if "category_id" in kwargs:
            category = EventCategory.by_id(kwargs.pop("category_id"))
        elif "category_tag" in kwargs:
            category = EventCategory.by_tag(kwargs.pop("category_tag"))
        else:
            category = None
        return fn(*args, category=category, **kwargs)

    return nufun