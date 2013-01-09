from json import dumps
from flask import Flask, make_response
from collections import OrderedDict
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from functools import wraps

import db_backend

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
api = restful.Api(app, decorators=[charset_fix_decorator])

@app.teardown_request
def shutdown_session(exception=None):
    """Cleanup the database session after a request.
    """
    db_backend.session.remove()


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


class TopicList(restful.Resource):
    def get(self, forum_id=None):
        guest_forums = db_backend.DbForums.guest_readable()
        guest_forum_ids = [f.id for f in guest_forums]

        topic_qry = db_backend.session.query(db_backend.DbTopics).filter(
            db_backend.DbTopics.forum_id.in_(guest_forum_ids)).order_by(db_backend.DbTopics.last_post.desc()).limit(100)

        topics = OrderedDict([(t.tid, t.title) for t in topic_qry])

        return topics


api.add_resource(TopicList, "/topics")

if __name__ == '__main__':
    app.debug = True
    app.run()
