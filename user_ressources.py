from functools import wraps
from flask import Flask, make_response, g, session, _request_ctx_stack, request
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from werkzeug.local import LocalProxy

import db_backend
from db_backend.user import ApiUser
import ipb_mess


debug = False

current_user = LocalProxy(lambda: _request_ctx_stack.top.user)


class Login(restful.Resource):
    """A resource to handle logins.
    """

    def get(self):
        if current_user.authenticated():
            return {"login": current_user.name}
        abort(400, message="Provide some data as post request!")

    def post(self):
        if current_user.authenticated():
            abort(400, message="Already logged in")

        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True, help="Need a Login!", location="form")
        parser.add_argument('password', type=str, required=True, help="Need a password!", location="form")
        args = parser.parse_args()

        user = db_backend.DbMembers.by_name(ipb_mess.ipb_clean_value(args["login"]))
        if user is None:
            abort(403, message="User not found!")

        if not user.password_valid(ipb_mess.ipb_clean_value(args["password"])):
            abort(403, message="Wrong password")

        if user.is_banned():
            abort(403, message="You are banned until %s" % user.ban.end.ctime())

        session["login_user_id"] = user.id

        return {"message": "Successfull logged in"}


class Logout(restful.Resource):
    """A resource to handle logouts.
    """

    def get(self):
        if not current_user.authenticated():
            abort(400, message="Not logged in!")

        del session["login_user_id"]
        return {"message": "Successfull logged out"}


def require_login(func):
    """A decorator to ensure that the decorated endpoint is only called from a valid user.

    For debugging the authentication requirement can be turned off using the debug flag
    of this module.

    :param func The endpoint to decorate.
    """

    @wraps(func)
    def nufun(*args, **kwargs):
        if not (debug or current_user.authenticated()):
            abort(401, message="authentication required")
        return func(*args, **kwargs)

    return nufun


def setup_auth(app, api):
    """Set up the authenticaton module for this app.

    :param app: The Flask app
    :param api: The Flask RESTful API
    """
    #ToDo: This has to be made more general to use it with other "modules" of the api.

    @app.before_request
    def load_user():
        ctx = _request_ctx_stack.top
        ctx.user = ApiUser()
        user_id = session.get("login_user_id")
        if user_id is not None:
            user = db_backend.DbMembers.by_id(user_id)
            if user is not None and not user.is_banned():
                ctx.user = user

    #todo: better session handling (permanent session, expiring, bla)

    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")

