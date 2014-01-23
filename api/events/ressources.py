from datetime import date, time, datetime, timedelta
from functools import wraps
from api.events import fieldsets
from dateutil.relativedelta import relativedelta
from flask.ext import restful

import db_backend
from db_backend.events import EventCategory
from flask.ext.restful import reqparse, abort
from flask.ext.restful_fieldsets import marshal_with_fieldset
from sqlalchemy.orm import joinedload


class EventInterval():
    max_interval = timedelta(days=100)

    def __init__(self):
        self._start = None
        self._end = None

    def _parse(self):
        parser = reqparse.RequestParser()
        parser.add_argument('since', type=int)
        parser.add_argument('before', type=int)
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
            end = datetime.combine(start.date() + relativedelta(day=1, months=+1),
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
        :return: eThe end date.
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


class EventList(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventFields)
    @_resolve_category
    def get(self, category=None):
        interval = EventInterval()

        event_qry = db_backend.DbEvents.query_between(interval.start,
                                                      interval.end)
        event_qry = event_qry.options(joinedload('topic'))
        if category is not None:
            event_qry = event_qry.filter(db_backend.DbEvents.category == category.id)

        event_list = []
        for event in event_qry:
            event_list.extend(event.instances_between(interval.start,
                                                      interval.end))

        return event_list


class EventCategoryList(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventCategoryFields)
    def get(self):
        return EventCategory.all_categories()


class Event(restful.Resource):
    pass


class LocationList(restful.Resource):
    pass


class Location(restful.Resource):
    pass


class OrganizerList(restful.Resource):
    pass


class Organizer(restful.Resource):
    pass