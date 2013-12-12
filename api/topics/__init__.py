from api.topics.ressources import TopicList, Topic, PostList
from flask import Blueprint
import flask_restful


def topic_blueprint():
    topic_bp = Blueprint("messages", __name__)

    topic_api = flask_restful.Api()
    topic_api.init_app(topic_bp)
    topic_api.add_resource(TopicList, "/")
    topic_api.add_resource(Topic, "/<int:topic_id>")
    topic_api.add_resource(PostList, "/<int:topic_id>/posts")

    return topic_bp