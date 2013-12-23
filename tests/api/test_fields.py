import unittest
from unittest.mock import MagicMock, PropertyMock
from api import fields as api_fields


class TestObjectMemberField(unittest.TestCase):
    def test_0010_simple_usage(self):
        my_mock = MagicMock()
        my_property = PropertyMock(return_value="XXX")
        type(my_mock).test = my_property
        my_field = api_fields.ObjectMemberField("test")

        formatted = my_field.format(my_mock)
        self.assertEqual(formatted, "XXX")
        self.assertTrue(my_property.called)

    def test_0020_no_attribute(self):
        my_mock = MagicMock(spec=str)
        my_field = api_fields.ObjectMemberField("test")

        formatted = my_field.format(my_mock)
        self.assertEqual(formatted, None)
