from api.events.ressources import EventList, EventCategoryList, LocationList, Event
from api.request_helper import charset_fix_decorator
from flask import Blueprint
import flask_restful


def event_blueprint():
    event_bp = Blueprint("events", __name__)

    event_api = flask_restful.Api(decorators=[charset_fix_decorator])
    event_api.init_app(event_bp)

    event_api.add_resource(EventList,"/", "/category/<int:category_id>", "/category/<category_tag>")
    event_api.add_resource(Event, "/<int:event_id>")
    event_api.add_resource(EventCategoryList, "/categories")
    event_api.add_resource(LocationList, "/locations")

    return event_bp