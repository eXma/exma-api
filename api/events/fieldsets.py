from flask.ext.restful import fields
from flask.ext.restful_fieldsets import Fieldset, OptionalNestedField


class EventCategoryFields(Fieldset):
    id = fields.Integer
    tag = fields.String
    name = fields.String


class EventLocationFields(Fieldset):
    id = fields.Integer(attribute="lid")
    name = fields.String(attribute="location")
    url = fields.String
    slug = fields.String(attribute="location_url")
    street = fields.String(attribute="strasse")
    zip_no = fields.String(attribute="plz")
    town = fields.String(attribute="stadt")


class EventFields(Fieldset):
    class Meta:
        default_embedd = []

    id = fields.Integer(attribute="event_id")
    title = fields.String
    start = fields.DateTime
    end = fields.DateTime
    editable = fields.Boolean
    allDay = fields.Boolean
    category = OptionalNestedField(EventCategoryFields, "tag", attribute="category_instance")
    location = OptionalNestedField(EventLocationFields, "lid", attribute="location")



