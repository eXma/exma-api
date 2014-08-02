from contextlib import contextmanager
import unittest
import datetime
from flask import Flask
from sqlalchemy.testing import mock
from werkzeug.exceptions import BadRequest

from api.events.request_parsing import _resolve_category, EventInterval
from db_backend.utils.events import EventCategory


# noinspection PyProtectedMember
class TestCategoryParsing(unittest.TestCase):
    def test_0010_category_id(self):
        @_resolve_category
        def dummy(category):
            return category

        all_events = EventCategory._event_categories
        for id in all_events:
            self.assertEqual(all_events[id], dummy(category_id=id))

    def test_0020_category_id_parsing_bad(self):
        @_resolve_category
        def dummy(category):
            return category

        all_events = EventCategory._event_categories
        category = dummy(category_id=max(all_events.keys()) + 2)

        self.assertEqual(-1, category.id)

    def test_0030_category_tag(self):
        @_resolve_category
        def dummy(category):
            return category

        all_tags = EventCategory._category_tags

        for tag in all_tags:
            self.assertEqual(all_tags[tag], dummy(category_tag=tag).id)

    def test_0040_category_tag_parsing_bad(self):
        @_resolve_category
        def dummy(category):
            return category

        self.assertEqual(-1, dummy(category_tag="XXX__XXX").id)

    def test_0050_no_category(self):
        @_resolve_category
        def dummy(category):
            return category

        self.assertIsNone(dummy())


class TestDateIntervalParsing(unittest.TestCase):
    @staticmethod
    @contextmanager
    def mocked_date(fixed_date):
        with mock.patch("api.events.request_parsing.date") as mock_date:
            mock_date.today.return_value = fixed_date
            mock_date.side_effect = lambda *args, **kw: datetime.date(*args, **kw)
            yield

    def test_0010_default_interval(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='', method="GET"):
                interval = EventInterval()
                self.assertEqual(interval.start, datetime.datetime(2000, 1, 1, 0, 0))
                self.assertEqual(interval.end, datetime.datetime(2000, 2, 1, 0, 0))

    def test_0020_only_end_interval(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='end=1010617200', method="GET"):
                interval = EventInterval()
                self.assertEqual(interval.start, datetime.datetime(2001, 12, 1, 0, 0))
                self.assertEqual(interval.end, datetime.datetime(2002, 1, 10, 0, 0))

    def test_0030_only_start_interval(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='start=1010617200', method="GET"):
                interval = EventInterval()
                self.assertEqual(interval.start, datetime.datetime(2002, 1, 10, 0, 0))
                self.assertEqual(interval.end, datetime.datetime(2002, 2, 10, 0, 0))

    def test_0040_start_and_end_interval(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='start=1010617200&end=1015714800', method="GET"):
                interval = EventInterval()
                self.assertEqual(interval.start, datetime.datetime(2002, 1, 10, 0, 0))
                self.assertEqual(interval.end, datetime.datetime(2002, 3, 10, 0, 0))

    def test_0050_interval_too_long(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='start=1010617200&end=1019343600', method="GET"):
                interval = EventInterval()
                self.assertRaises(BadRequest, interval._parse)

    def test_0050_end_before_start(self):
        app = Flask(__name__)
        with self.mocked_date(datetime.date(2000, 1, 10)):
            with app.test_request_context('/bubble', query_string='end=1010617200&start=1015714800', method="GET"):
                interval = EventInterval()
                self.assertRaises(BadRequest, interval._parse)
