from json import dumps
from flask import Flask, make_response, g, session
from collections import OrderedDict
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from functools import wraps

import db_backend
import user_ressources

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
Flask.secret_key = r"af4thei1VaongahB7eiloo]Push@ieZohz{ohjo?w&ahxaegh2zood0rie3i"

api = restful.Api(app, decorators=[charset_fix_decorator])

@app.teardown_request
def shutdown_session(exception=None):
    """Cleanup the database session after a request.
    """
    db_backend.session.remove()

user_ressources.setup_auth(app, api)

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



def limit_query(query, req_args):
    limit = req_args.get("limit")
    offset = req_args.get("offset")
    if limit is not None and limit > 0:
        query = query.limit(limit)
    if offset is not None and offset > 0:
        query = query.offset(offset)
    return query



class TopicList(restful.Resource):
    def get(self, forum_id=None):

        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int)
        parser.add_argument('offset', type=int)
        args = parser.parse_args()

        guest_forums = db_backend.DbForums.guest_readable()
        guest_forum_ids = [f.id for f in guest_forums]

        topic_qry = db_backend.session.query(db_backend.DbTopics).filter(
            db_backend.DbTopics.forum_id.in_(guest_forum_ids)).filter_by(approved=1).order_by(db_backend.DbTopics.last_post.desc()).limit(100)
        topic_qry = limit_query(topic_qry, args)
        topics = OrderedDict([(t.tid, t.title) for t in topic_qry])

        return topics




api.add_resource(TopicList, "/topics")

if __name__ == '__main__':
    app.debug = True
    app.run()
