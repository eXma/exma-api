from db_backend.utils.user import ApiUser
from flask.ext.restful import abort
from functools import wraps
from werkzeug.local import LocalProxy

debug = False

current_user = LocalProxy(lambda: _request_ctx_stack.top.user)
from flask import session, _request_ctx_stack


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


def setup_auth(app, user_lookup):
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
            user = user_lookup(user_id)
            if user is not None and not user.is_banned():
                ctx.user = user

                #todo: better session handling (permanent session, expiring, bla)
