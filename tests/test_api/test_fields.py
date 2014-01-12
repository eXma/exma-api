import unittest
from unittest.mock import MagicMock, PropertyMock
from api import fields as api_fields
from flask.ext.restful import fields


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

    def test_0030_member_field(self):
        my_mock = MagicMock()
        my_property = PropertyMock(return_value=2)
        type(my_mock).test = my_property

        my_field1 = api_fields.ObjectMemberField("test")
        self.assertEqual(my_field1.format(my_mock), 2)

        my_field2 = api_fields.ObjectMemberField("test", member_field=fields.String)
        self.assertEqual(my_field2.format(my_mock), "2")

        my_field3 = api_fields.ObjectMemberField("test", member_field=fields.Integer)
        self.assertEqual(my_field3.format(my_mock), 2)

        my_field2 = api_fields.ObjectMemberField("test", member_field=fields.String())
        self.assertEqual(my_field2.format(my_mock), "2")


class TestOptionalNestedField(unittest.TestCase):
    def test_0010_nested_usage(self):
        my_mock = MagicMock()
        my_property = PropertyMock(return_value=2)
        type(my_mock).test = my_property

        instance = api_fields.OptionalNestedField("NESTED", "test")

        self.assertEqual(instance.nested_fieldset(), "NESTED")
        self.assertIsInstance(instance.key_field(), api_fields.ObjectMemberField)
        self.assertEqual(instance.key_field().format(my_mock), 2)

    def test_0020_no_nested_key(self):
        my_mock = MagicMock()
        my_property = PropertyMock(return_value=2)
        type(my_mock).test = my_property

        instance = api_fields.OptionalNestedField("NESTED", None)

        self.assertEqual(instance.nested_fieldset(), "NESTED")
        self.assertEqual(instance.key_field(), None)

    def test_0030_plain_field_type(self):
        my_mock = MagicMock()
        my_property = PropertyMock(return_value=2)
        type(my_mock).test = my_property

        instance = api_fields.OptionalNestedField("NESTED", "test", plain_field=fields.String)

        self.assertEqual(instance.nested_fieldset(), "NESTED")
        self.assertIsInstance(instance.key_field(), api_fields.ObjectMemberField)
        self.assertEqual(instance.key_field().format(my_mock), "2")
