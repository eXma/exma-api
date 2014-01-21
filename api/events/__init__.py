from api.events.ressources import EventList
from api.request_helper import charset_fix_decorator
from flask import Blueprint
import flask_restful


def event_blueprint():
    event_bp = Blueprint("events", __name__)

    event_api = flask_restful.Api(decorators=[charset_fix_decorator])
    event_api.init_app(event_bp)

    event_api.add_resource(EventList, "/")

    return event_bp