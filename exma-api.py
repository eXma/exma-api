from json import dumps
from flask import Flask, make_response, g, session
from collections import OrderedDict
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from functools import wraps
from sqlalchemy.orm.exc import NoResultFound

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
    resp.headers["Access-Control-Allow-Origin"] = "*"
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

topic_fields = {
    'tid': fields.Integer,
    'title': fields.String,
    'last_post': fields.String,
    'last_poster_name': fields.String,
    'starter_name': fields.String
}


class TopicList(restful.Resource):
    @marshal_with(topic_fields)
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

        topics = topic_qry.all()

        return topics

post_fields = {
    'pid': fields.Integer,
    'post': fields.String,
    'author_name': fields.String,
    'post_date': fields.String,
}

class PostList(restful.Resource):
    @marshal_with(post_fields)
    def get(self, topic_id):
        topic = db_backend.DbTopics.by_id(topic_id, user_ressources.current_user.perm_masks)
        if topic is None:
            abort(404, message="No topic with this id available")

        posts = db_backend.DbPosts.by_topic_query(topic_id).limit(40)
        return posts.all()


class Topic(restful.Resource):
    @marshal_with(topic_fields)
    def get(self, topic_id):
        topic = db_backend.DbTopics.by_id(topic_id, user_ressources.current_user.perm_masks)
        if topic is None:
            abort(404, message="No topic with this id available")
        return topic


picture_fileds = {
    "id": fields.Integer(attribute="pid"),
    "album_id": fields.Integer,
    "hits": fields.Integer,
    "url": fields.String,
    "thumb_small_url": fields.String,
    "thumb_url": fields.String
}

album_fields = {
    'id': fields.Integer(attribute="a_id"),
    'title': fields.String,
    'thumbnail': fields.Nested(picture_fileds),
    'post_date': fields.String,
    }


class AlbumList(restful.Resource):
    @marshal_with(album_fields)
    def get(self):
        albums_qry = db_backend.session.query(db_backend.DbPixAlbums).order_by(db_backend.DbPixAlbums.time.desc())
        all = albums_qry.all()


        return all



api.add_resource(TopicList, "/topics")
api.add_resource(Topic, "/topics/<int:topic_id>")
api.add_resource(PostList, "/topics/<int:topic_id>/posts")


api.add_resource(AlbumList, "/albums")


if __name__ == '__main__':
    app.debug = True
    app.run("0.0.0.0")
