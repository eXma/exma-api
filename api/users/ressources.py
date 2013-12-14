from api.user.authorization import current_user
import db_backend
from flask import session
from flask.ext import restful
from flask.ext.restful import abort, reqparse
import ipb_mess


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

        return {"message": "Successful logged in"}


class Logout(restful.Resource):
    """A resource to handle logouts.
    """

    def get(self):
        if not current_user.authenticated():
            abort(400, message="Not logged in!")

        del session["login_user_id"]
        return {"message": "Successful logged out"}
