from flask.ext.restful.representations import json


def configure_default_json():
    json.settings.setdefault("ensure_ascii", False)
