from api import user, messages, albums, topics
from api.user import authorization
from flask import Flask, request
from flask.ext import restful
from functools import wraps

import db_backend
import pixma_images


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



@app.route('/')
def start():
    return 'eXma REST API!'


app.register_blueprint(pixma_images.pixma_blueprint(), url_prefix="/piXma")
app.register_blueprint(topics.topic_blueprint(), url_prefix="/topics")
app.register_blueprint(albums.album_blueprint(), url_prefix="/messages")
app.register_blueprint(messages.message_blueprint(), url_prefix="/messages")

if __name__ == '__main__':
    #user_ressources.debug = True
    app.debug = True
    app.run("0.0.0.0")
