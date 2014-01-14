from flask.ext.restful import fields
from flask.ext.restful_fieldsets import Fieldset, OptionalNestedField
from api.fields import PixmaUrl


class PictureFields(Fieldset):
    id = fields.Integer(attribute="pid"),
    album_id = fields.Integer,
    hits = fields.Integer,
    url = PixmaUrl(),
    thumb_small_url = PixmaUrl(format_type=PixmaUrl.thumb_small),
    thumb_square_url = PixmaUrl(format_type=PixmaUrl.thumb_square),
    thumb_url = PixmaUrl(format_type=PixmaUrl.thumb)


class AlbumFields(Fieldset):
    id = fields.Integer(attribute="a_id"),
    title = fields.String,
    thumbnail = OptionalNestedField(PictureFields, "id", plain_field=fields.Integer)
    date = fields.String(attribute="a_date"),
    location_name = fields.String(attribute='a_location'),
    description = fields.String(attribute='a_desc')
