import unittest
from unittest.mock import patch
from api import fieldset
from flask import Flask
from flask.ext.restful import fields
from api import fields as api_fields


# noinspection PyProtectedMember
class TestSimpleFieldset(unittest.TestCase):
    def test_0010_empty(self):
        class MyFieldset(fieldset.Fieldset):
            pass

        dummy = MyFieldset()

        self.assertIsInstance(dummy.meta, fieldset.DefaultMeta)
        self.assertEqual(len(dummy._fields), 0)
        self.assertIsInstance(dummy._fields, dict)
        self.assertEqual(len(dummy._nested), 0)
        self.assertIsInstance(dummy._nested, list)
        self.assertEqual(len(dummy._nested_recursive), 0)
        self.assertIsInstance(dummy._nested_recursive, list)
        self.assertEqual(len(dummy._fields_recursive), 0)
        self.assertIsInstance(dummy._fields_recursive, list)
        self.assertEqual(len(dummy._default_fields), 0)
        self.assertIsInstance(dummy._default_fields, set)
        self.assertEqual(len(dummy._default_embedd), 0)
        self.assertIsInstance(dummy._default_embedd, set)

        self.assertEqual(dummy.marshall_dict(), {})

    def test_0020_simple_fields(self):
        class MyFieldset(fieldset.Fieldset):
            test01 = fields.Integer
            test02 = fields.Float
            test03 = str
            test04 = fields.Boolean

        dummy = MyFieldset()

        self.assertIsInstance(dummy.meta, fieldset.DefaultMeta)
        self.assertEqual(len(dummy._fields), 3)
        self.assertIsInstance(dummy._fields, dict)
        self.assertIn("test01", dummy._fields)
        self.assertIn("test02", dummy._fields)
        self.assertNotIn("test03", dummy._fields)
        self.assertIn("test04", dummy._fields)
        self.assertEqual(len(dummy._nested), 0)
        self.assertIsInstance(dummy._nested, list)
        self.assertEqual(len(dummy._nested_recursive), 0)
        self.assertIsInstance(dummy._nested_recursive, list)
        self.assertEqual(len(dummy._fields_recursive), 3)
        self.assertIsInstance(dummy._fields_recursive, list)
        self.assertIn("test01", dummy._fields_recursive)
        self.assertIn("test02", dummy._fields_recursive)
        self.assertNotIn("test03", dummy._fields_recursive)
        self.assertIn("test04", dummy._fields_recursive)
        self.assertEqual(len(dummy._default_fields), 3)
        self.assertIn("test01", dummy._default_fields)
        self.assertIn("test02", dummy._default_fields)
        self.assertNotIn("test03", dummy._default_fields)
        self.assertIn("test04", dummy._default_fields)
        self.assertIsInstance(dummy._default_fields, set)
        self.assertEqual(len(dummy._default_embedd), 0)
        self.assertIsInstance(dummy._default_embedd, set)

        marshall = dummy.marshall_dict()
        self.assertIsInstance(marshall, dict)
        self.assertEqual(len(marshall), 3)
        self.assertIn("test01", marshall)
        self.assertEqual(marshall["test01"], dummy.test01)
        self.assertIn("test02", marshall)
        self.assertEqual(marshall["test02"], dummy.test02)
        self.assertNotIn("test03", marshall)
        self.assertIn("test04", marshall)
        self.assertEqual(marshall["test04"], dummy.test04)

        marshall = dummy.marshall_dict(selected_fields={"test01", "test02"})
        self.assertIsInstance(marshall, dict)
        self.assertEqual(len(marshall), 2)
        self.assertIn("test01", marshall)
        self.assertEqual(marshall["test01"], dummy.test01)
        self.assertIn("test02", marshall)
        self.assertEqual(marshall["test02"], dummy.test02)
        self.assertNotIn("test03", marshall)
        self.assertNotIn("test04", marshall)

    def test_0030_defaults(self):
        class MyFieldset(fieldset.Fieldset):
            class Meta:
                default_fields = ["test01", "test04"]

            test01 = fields.Integer
            test02 = fields.Float
            test03 = str
            test04 = fields.Boolean

        dummy = MyFieldset()

        self.assertIsInstance(dummy.meta, fieldset.DefaultMeta)
        self.assertEqual(len(dummy._fields), 3)
        self.assertIsInstance(dummy._fields, dict)
        self.assertIn("test01", dummy._fields)
        self.assertIn("test02", dummy._fields)
        self.assertNotIn("test03", dummy._fields)
        self.assertIn("test04", dummy._fields)
        self.assertEqual(len(dummy._nested), 0)
        self.assertIsInstance(dummy._nested, list)
        self.assertEqual(len(dummy._nested_recursive), 0)
        self.assertIsInstance(dummy._nested_recursive, list)
        self.assertEqual(len(dummy._fields_recursive), 3)
        self.assertIsInstance(dummy._fields_recursive, list)
        self.assertIn("test01", dummy._fields_recursive)
        self.assertIn("test02", dummy._fields_recursive)
        self.assertNotIn("test03", dummy._fields_recursive)
        self.assertIn("test04", dummy._fields_recursive)
        self.assertEqual(len(dummy._default_fields), 2)
        self.assertIn("test01", dummy._default_fields)
        self.assertNotIn("test02", dummy._default_fields)
        self.assertNotIn("test03", dummy._default_fields)
        self.assertIn("test04", dummy._default_fields)
        self.assertIsInstance(dummy._default_fields, set)
        self.assertEqual(len(dummy._default_embedd), 0)
        self.assertIsInstance(dummy._default_embedd, set)

        marshall = dummy.marshall_dict()
        self.assertIsInstance(marshall, dict)
        self.assertEqual(len(marshall), 2)
        self.assertIn("test01", marshall)
        self.assertEqual(marshall["test01"], dummy.test01)
        self.assertNotIn("test02", marshall)
        self.assertNotIn("test03", marshall)
        self.assertIn("test04", marshall)
        self.assertEqual(marshall["test04"], dummy.test04)

        marshall = dummy.marshall_dict(selected_fields={"test01", "test02"})
        self.assertIsInstance(marshall, dict)
        self.assertEqual(len(marshall), 2)
        self.assertIn("test01", marshall)
        self.assertEqual(marshall["test01"], dummy.test01)
        self.assertIn("test02", marshall)
        self.assertEqual(marshall["test02"], dummy.test02)
        self.assertNotIn("test03", marshall)
        self.assertNotIn("test04", marshall)


# noinspection PyProtectedMember
class TestSimpleFieldsetRequestParsing(unittest.TestCase):
    def test_0010_empty_set_empty(self):
        class MyFieldset(fieldset.Fieldset):
            pass

        dummy = MyFieldset()
        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=', method="GET"):
            parsed = dummy._parse_request_overrides()
            self.assertEquals(parsed, (None, None))

    def test_0020_empty_set_missing(self):
        class MyFieldset(fieldset.Fieldset):
            pass

        dummy = MyFieldset()
        app = Flask(__name__)
        with app.test_request_context('/bubble', method="GET"):
            parsed = dummy._parse_request_overrides()
            self.assertEquals(parsed, (None, None))

    # noinspection PyMethodMayBeStatic
    @patch('flask_restful.abort')
    def test_0030_empty_set_unknown(self, abort):
        class MyFieldset(fieldset.Fieldset):
            pass

        dummy = MyFieldset()
        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string="fields=test01,test02", method="GET"):
            dummy._parse_request_overrides()

        abort.assert_called_with(400, message='Unknown fields: test01, test02')

    def test_0040_simple_set_known(self):
        class MyFieldset(fieldset.Fieldset):
            test01 = fields.Boolean
            test02 = fields.Integer

        dummy = MyFieldset()
        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=test01,test02', method="GET"):
            parsed = dummy._parse_request_overrides()
            self.assertEquals(parsed, ({"test01", "test02"}, None))

    # noinspection PyMethodMayBeStatic
    @patch('flask_restful.abort')
    def test_0050_simple_set_unknown(self, abort):
        class MyFieldset(fieldset.Fieldset):
            test01 = fields.Boolean
            test02 = fields.Integer

        dummy = MyFieldset()
        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string="fields=test01,test03", method="GET"):
            dummy._parse_request_overrides()

        abort.assert_called_with(400, message='Unknown fields: test03')


class TestSimpleFieldsetMarshallDecorator(unittest.TestCase):
    def test_0010_empty_set(self):
        class MyFieldset(fieldset.Fieldset):
            pass

        @MyFieldset.do_marshall()
        def foo():
            return {"test01": 1, "test02": "bla", "test04": False}

        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=', method="GET"):
            result = foo()
            self.assertEqual(result, {})

    def test_0020_full_set(self):
        class MyFieldset(fieldset.Fieldset):
            test01 = fields.Integer
            test02 = fields.String
            test04 = fields.Boolean

        @MyFieldset.do_marshall()
        def foo():
            return {"test01": 1, "test02": "bla", "test03": 3, "test04": False}

        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=', method="GET"):
            result = foo()
            self.assertEqual(len(result), 3)
            self.assertIn("test01", result)
            self.assertIn("test02", result)
            self.assertIn("test04", result)

    def test_0030_default_set(self):
        class MyFieldset(fieldset.Fieldset):
            class Meta:
                default_fields = ["test01", "test04"]

            test01 = fields.Integer
            test02 = fields.String
            test04 = fields.Boolean

        @MyFieldset.do_marshall()
        def foo():
            return {"test01": 1, "test02": "bla", "test03": 3, "test04": False}

        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=', method="GET"):
            result = foo()
            self.assertEqual(len(result), 2)
            self.assertIn("test01", result)
            self.assertIn("test04", result)

    def test_0040_query_set(self):
        class MyFieldset(fieldset.Fieldset):
            class Meta:
                default_fields = ["test01", "test04"]

            test01 = fields.Integer
            test02 = fields.String
            test04 = fields.Boolean

        @MyFieldset.do_marshall()
        def foo():
            return {"test01": 1, "test02": "bla", "test03": 3, "test04": False}

        app = Flask(__name__)
        with app.test_request_context('/bubble', query_string='fields=test01,test02', method="GET"):
            result = foo()
            self.assertEqual(len(result), 2)
            self.assertIn("test01", result)
            self.assertIn("test02", result)


class TestNestedFieldset(unittest.TestCase):
    def test_simple_setup(self):
        class SimpleNestedFieldset(fieldset.Fieldset):
            nest01 = fields.Integer
            nest02 = fields.Boolean

        class MyFieldSet(fieldset.Fieldset):
            test01 = fields.Boolean
            test02 = api_fields.OptionalNestedField(SimpleNestedFieldset, None, None)

        dummy = MyFieldSet()
        self.assertEqual(dummy.marshall_dict(), {"test01": MyFieldSet.test01,
                                                 "test02": {"nest01": SimpleNestedFieldset.nest01,
                                                            "nest02": SimpleNestedFieldset.nest02}})
