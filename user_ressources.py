from functools import wraps
from flask import Flask, make_response, g, session, _request_ctx_stack
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from werkzeug.local import LocalProxy

import db_backend
from db_backend.user import ApiUser


debug = False

current_user = LocalProxy(lambda: _request_ctx_stack.top.user)

class Login(restful.Resource):
    def get(self):
        abort(400, message=u"Provide some data as post request!")

    def post(self):
        if current_user.authenticated():
            abort(400, message=u"Already logged in")

        parser = reqparse.RequestParser()
        parser.add_argument('login', type=unicode, required=True, help=u"Need a Login!")
        parser.add_argument('password', type=unicode, required=True, help=u"Need a password!")
        args = parser.parse_args()

        user = db_backend.DbMembers.by_name(args["login"])
        if user is None:
            abort(403, message=u"User not found!")

        if not user.password_valid(args["password"]):
            abort(403, message=u"Wrong password")

        if user.is_banned():
            abort(403, message=u"You are banned until %s" % user.ban.end.ctime())

        session["login_user_id"] = user.id

        return {"message": u"Successfull logged in"}


class Logout(restful.Resource):
    def get(self):
        if not current_user.authenticated():
            abort(400, message=u"Not logged in!")

        del session["login_user_id"]
        return {"message": u"Successfull logged out"}


def require_login(func):
    @wraps(func)
    def nufun(*args, **kwargs):
        if not (debug or current_user.authenticated()):
            abort(401, message="authentication required")
        return func(*args, **kwargs)

    return nufun


def setup_auth(app, api):
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

