from flask.ext.restful import fields
from flask.ext.restful_fieldsets import Fieldset


class MemberFields(Fieldset):
    id = fields.Integer(attribute="id")
    name = fields.String
    post_count = fields.Integer(attribute="posts")