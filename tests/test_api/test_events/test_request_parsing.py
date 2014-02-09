import unittest

from api.events.request_parsing import _resolve_category
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