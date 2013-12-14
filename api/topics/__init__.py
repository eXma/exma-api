from api.representation import set_unicode_json_repesentation
from api.request_helper import charset_fix_decorator
from api.topics.ressources import TopicList, Topic, PostList
from flask import Blueprint
import flask_restful


def topic_blueprint():
    topic_bp = Blueprint("topics", __name__)

    topic_api = flask_restful.Api(decorators=[charset_fix_decorator])
    topic_api.init_app(topic_bp)
    set_unicode_json_repesentation(topic_api)

    topic_api.add_resource(TopicList, "/")
    topic_api.add_resource(Topic, "/<int:topic_id>")
    topic_api.add_resource(PostList, "/<int:topic_id>/posts")

    return topic_bp