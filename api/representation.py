from json import dumps
from flask import make_response


def set_unicode_json_repesentation(api):
    api.representation('application/json')(unicode_json_representation)


def unicode_json_representation(data, code, headers=None):
    """This is a "enhanced" json representation handler that leaves unicode unicode.

    :param data: The data to pack in a response
    :param code: The http status code.
    :param headers: Optional additional headers
    :return: A new fresh response.
    """
    resp = make_response(dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp