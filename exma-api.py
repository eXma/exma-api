from json import dumps
from api import user, messages, albums, topics
from api.user import authorization
from flask import Flask, make_response, send_from_directory, request, send_file
from flask.ext.restful import abort
from flask.ext import restful
from functools import wraps
import os

import db_backend
import thumbnailer


def charset_fix_decorator(response_func):
    """Fix the output mime-type by adding the charset information.
    """

    @wraps(response_func)
    def wrapper(*args, **kwargs):
        response = response_func(*args, **kwargs)
        if ("charset" not in response.headers['Content-Type']):
            response.headers['Content-Type'] += "; charset=UTF-8"
        return response

    return wrapper


app = Flask(__name__)
Flask.secret_key = r"af4thei1VaongahB7eiloo]Push@ieZohz{o2hjo?w&ahxaegh2zood0rie3i"

api = restful.Api(app, decorators=[charset_fix_decorator])


@app.teardown_request
def shutdown_session(exception=None):
    """Cleanup the database session after a request.
    """
    db_backend.session.remove()


@app.after_request
def add_cors_header(resp):
    #resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin") or "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept"
    del resp.headers['WWW-Authenticate'] # = 'Basic realm="flask-restful'
    return resp


authorization.setup_auth(app)
app.register_blueprint(user.user_blueprint())


@api.representation('application/json')
def unicode_json_representation(data, code, headers=None):
    """This is a "enhanced" json representation handler that leaves unicode unicode.

    :param data: The data to pack in a response
    :param code: The http status code.
    :param headers: Optional additional headers
    :return: A new fresh response.
    """
    resp = make_response(dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


@app.route('/')
def start():
    return 'eXma REST API!'


@app.route("/piXma/<int:pic_id>.jpg", defaults={"type_string": None})
@app.route("/piXma/<int:pic_id>_<string:type_string>.jpg")
@authorization.require_login
def send_picture(pic_id, type_string):
    """Sends an image to the client if authorized.

    :type pic_id: int
    :type type_string: str or None
    """
    pic = db_backend.DbPixPics.by_id(pic_id)
    if pic is None:
        abort(404)

    filename = "%d.jpg" % pic_id
    if type_string is not None:
        if type_string not in ("st", "bt", "sq"):
            abort(404)
        if type_string == "sq":
            filename = "%d_bt.jpg" % (pic_id,)
        else:
            filename = "%d_%s.jpg" % (pic_id, type_string)
    else:
        pic.hits += 1
        db_backend.session.commit()

    filepath = os.path.join("/mnt/tmp", filename)
    if not os.path.isfile(filepath):
        abort(404)

    if (type_string == "sq"):
        handle = thumbnailer.load_square_resized(filepath)
        return send_file(handle, mimetype="image/jpeg")

    return send_from_directory("/mnt/tmp", filename)


app.register_blueprint(topics.topic_blueprint(), url_prefix="/topics")
app.register_blueprint(albums.album_blueprint(), url_prefix="/messages")
app.register_blueprint(messages.message_blueprint(), url_prefix="/messages")

if __name__ == '__main__':
    #user_ressources.debug = True
    app.debug = True
    app.run("0.0.0.0")
