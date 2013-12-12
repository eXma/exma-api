from api.user.ressources import Login, Logout
from flask import Blueprint
import flask_restful


def user_blueprint():
    user_bp = Blueprint("user", __name__)

    user_api = flask_restful.Api()
    user_api.init_app(user_bp)

    user_api.add_resource(Login, "/login")
    user_api.add_resource(Logout, "/logout")