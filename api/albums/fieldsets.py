from flask.ext.restful import fields
from api.fields import PixmaUrl

picture_fileds = {
    "id": fields.Integer(attribute="pid"),
    "album_id": fields.Integer,
    "hits": fields.Integer,
    "url": PixmaUrl(),
    "thumb_small_url": PixmaUrl(format_type=PixmaUrl.thumb_small),
    "thumb_square_url": PixmaUrl(format_type=PixmaUrl.thumb_square),
    "thumb_url": PixmaUrl(format_type=PixmaUrl.thumb)
}

album_fields = {
    'id': fields.Integer(attribute="a_id"),
    'title': fields.String,
    'thumbnail': fields.Nested(picture_fileds),
    'date': fields.String(attribute="a_date"),
    'location_name': fields.String(attribute='a_location'),
    'description': fields.String(attribute='a_desc')
}