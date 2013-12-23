from flask.ext.restful import fields
from api.fields import LazyNestedField, UsernameField, ObjectMemberField

body_fields = {
    'id': fields.Integer(attribute="msg_id"),
    'text': fields.String(attribute="msg_post")
}

message_fields = {
    'id': fields.Integer(attribute="mt_id"),
    'title': fields.String(attribute='mt_title'),
    'date': fields.Integer(attribute="mt_date"),
    'from': ObjectMemberField(member="name", attribute="from_user"),
    'to': ObjectMemberField(member="name", attribute="to_user"),
    'folder': fields.String(attribute="mt_vid_folder"),
    'body': LazyNestedField(body_fields)
}

folder_fields = {
    "name": fields.String,
    "id": fields.String(attribute="identifier"),
    "count": fields.Integer(attribute="message_count"),
}