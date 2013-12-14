from api.messages.ressources import MessageList, Message, FolderList
from api.representation import set_unicode_json_repesentation
from api.request_helper import charset_fix_decorator
from flask import Blueprint
import flask_restful


def message_blueprint():
    message_bp = Blueprint("messages", __name__)

    message_api = flask_restful.Api(decorators=[charset_fix_decorator])
    message_api.init_app(message_bp)
    set_unicode_json_repesentation(message_api)

    message_api.add_resource(MessageList, "/", "/folder/<folder_id>")
    message_api.add_resource(Message, "/single/<message_topic_id>")
    message_api.add_resource(FolderList, "/folder")

    return message_bp