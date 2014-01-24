from flask.ext.restful import fields
from flask.ext.restful_fieldsets import Fieldset, OptionalNestedField


class EventCategoryFields(Fieldset):
    id = fields.Integer
    tag = fields.String
    name = fields.String


class EventFields(Fieldset):
    id = fields.Integer(attribute="event_id")
    title = fields.String
    start = fields.DateTime
    end = fields.DateTime
    editable = fields.Boolean
    allDay = fields.Boolean
    category = OptionalNestedField(EventCategoryFields, "tag", attribute="category_instance")



