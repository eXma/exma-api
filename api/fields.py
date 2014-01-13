from pprint import pformat
from flask import url_for, request
from flask.ext.restful import fields, marshal
from flask.ext.restful.fields import to_marshallable_type


class LazyNestedField(fields.Nested):
    """This os a nested field that returns None if the key does not exist.

    The original raises an error in this case.
    """

    def output(self, key, obj):
        data = to_marshallable_type(obj)
        if self.attribute is not None:
            key = self.attribute
        if key not in data:
            return None
        return marshal(data[key], self.nested)



class PixmaUrl(fields.Raw):
    """This is a output marshal field to encode image urls in different formats.
    """
    thumb = "bt"
    thumb_small = "st"
    thumb_square = "sq"

    def __init__(self, format_type=None, attribute="pid"):
        """
        :param format_type: The format of the image. Should be one of ("st", "bt", "sq")
        :type format_type: str
        :param attribute: The attribute to look for the id-part of the image url.
        :type attribute: str
        """
        super(PixmaUrl, self).__init__(attribute=attribute)
        self.format_type = format_type

    def format(self, value):
        """Formats the input to a url.

        :type value: long
        :return: The absolute url for the image.
        :rtype: str
        """
        if self.format_type is None:
            path = url_for("send_picture", pic_id=value).lstrip("/")
        else:
            path = url_for("send_picture", pic_id=value, type_string=self.format_type).lstrip("/")
        return "/".join((request.url_root.rstrip("/"), path))
