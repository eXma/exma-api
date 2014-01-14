from flask.ext.restful import fields
from flask.ext.restful_fieldsets import ObjectMemberField, Fieldset, OptionalNestedField


class BodyFields(Fieldset):
    id = fields.Integer(attribute="msg_id")
    text = fields.String(attribute="msg_post")


class MessageFields(Fieldset):
    id = fields.Integer(attribute="mt_id")
    title = fields.String(attribute='mt_title')
    date = fields.Integer(attribute="mt_date")
    from_name = ObjectMemberField(member="name", attribute="from_user")
    to_name = ObjectMemberField(member="name", attribute="to_user")
    folder = fields.String(attribute="mt_vid_folder")
    body = OptionalNestedField(BodyFields, "msg_id", plain_field=fields.Integer)


class FolderFields(Fieldset):
    name = fields.String,
    id = fields.String(attribute="identifier"),
    count = fields.Integer(attribute="message_count"),
