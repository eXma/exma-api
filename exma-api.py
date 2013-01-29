from json import dumps
from flask import Flask, make_response, g, session, send_from_directory, request, url_for, send_file
from collections import OrderedDict
from flask.ext.restful import fields, marshal_with, abort, reqparse
from flask.ext import restful
from functools import wraps
from sqlalchemy.orm.exc import NoResultFound
import os

import db_backend
import user_ressources
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


@app.route("/piXma/<int:pic_id>.jpg", defaults={"type_string": None})
@app.route("/piXma/<int:pic_id>_<string:type_string>.jpg")
@user_ressources.require_login
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


def limit_query(query):
    """Apply the limit/offset querystring args.

    :param query: The query to limit.
    :type query: sqlalchemy.orm.query.Query
    :return: The limited query.
    :rtype : sqlalchemy.orm.query.Query
    """

    parser = reqparse.RequestParser()
    parser.add_argument('limit', type=int)
    parser.add_argument('offset', type=int)
    req_args = parser.parse_args()

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
        guest_forums = db_backend.DbForums.guest_readable()
        guest_forum_ids = [f.id for f in guest_forums]

        topic_qry = db_backend.session.query(db_backend.DbTopics).filter(
            db_backend.DbTopics.forum_id.in_(guest_forum_ids)).filter_by(approved=1).order_by(
            db_backend.DbTopics.last_post.desc()).limit(100)
        topic_qry = limit_query(topic_qry)

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


class PixmaUrl(fields.Raw):
    """This is a output marshal field to encode image urls in different formats.
    """
    thumb = "bt"
    thumb_small = "st"
    thumb_square = "sq"

    def __init__(self, format_type=None, attribute="pid"):
        """
        :param format_type: The format of the image. Should be one of ("st", "bt", "sq")
        :type format_type: str
        :param attribute: The attribute to look for the id-part of the image url.
        :type attribute: str
        """
        super(PixmaUrl, self).__init__(attribute=attribute)
        self.format_type = format_type

    def format(self, value):
        """Formats the input to a url.

        :type value: long
        :return: The absolute url for the image.
        :rtype: str
        """
        if self.format_type is None:
            path = url_for("send_picture", pic_id=value).lstrip("/")
        else:
            path = url_for("send_picture", pic_id=value, type_string=self.format_type).lstrip("/")
        return "/".join((request.url_root.rstrip("/"), path))


picture_fileds = {
    "id": fields.Integer(attribute="pid"),
    "album_id": fields.Integer,
    "hits": fields.Integer,
    "url": PixmaUrl(),
    "thumb_small_url": PixmaUrl(format_type=PixmaUrl.thumb_small),
    "thumb_square_url": PixmaUrl(format_type=PixmaUrl.thumb_square),
    "thumb_url": PixmaUrl(format_type=PixmaUrl.thumb)
}

album_fields = {
    'id': fields.Integer(attribute="a_id"),
    'title': fields.String,
    'thumbnail': fields.Nested(picture_fileds),
    'date': fields.String(attribute="a_date"),
    'location_name': fields.String(attribute='a_location'),
    'description': fields.String(attribute='a_desc')
}


class AlbumList(restful.Resource):
    @user_ressources.require_login
    @marshal_with(album_fields)
    def get(self):
        albums_qry = db_backend.session.query(db_backend.DbPixAlbums).order_by(db_backend.DbPixAlbums.time.desc())
        albums_qry = limit_query(albums_qry)

        return albums_qry.all()


class Album(restful.Resource):
    @user_ressources.require_login
    @marshal_with(album_fields)
    def get(self, album_id):
        album = db_backend.DbPixAlbums.by_id(album_id)
        if album is None:
            return abort(404, message="Album not found")
        return album


class PictureList(restful.Resource):
    @user_ressources.require_login
    @marshal_with(picture_fileds)
    def get(self, album_id):
        album = db_backend.DbPixAlbums.by_id(album_id)
        if album is None:
            abort(404, message="album not found")

        return album.pictures


class UsernameField(fields.Raw):
    """Filter out the username from a members object
    """
    def format(self, value):
        if not isinstance(value, db_backend.DbMembers):
            return None
        return value.name


message_fields = {
    'id': fields.Integer(attribute="mt_id"),
    'title': fields.String(attribute='mt_title'),
    'date': fields.Integer(attribute="mt_date"),
    'from': UsernameField(attribute="from_user"),
    'to': UsernameField(attribute="to_user"),
    'folder': fields.String(attribute="mt_vid_folder")
}

class MessageList(restful.Resource):
    @user_ressources.require_login
    @marshal_with(message_fields)
    def get(self, folder_id=None):

        parser = reqparse.RequestParser()
        parser.add_argument('since', type=int)
        parser.add_argument('before', type=int)
        req_args = parser.parse_args()

        message_qry = db_backend.DbMessageTopics.for_user(user_ressources.current_user).order_by(db_backend.DbMessageTopics.mt_date.desc())

        if req_args.get("since") is not None:
            message_qry = message_qry.filter(db_backend.DbMessageTopics.mt_id > req_args["since"])
        if req_args.get("before") is not None:
            message_qry = message_qry.filter(db_backend.DbMessageTopics.mt_id > req_args["before"])

        if folder_id is not None:
            message_qry = message_qry.filter_by(mt_vid_folder=folder_id)
        message_qry = limit_query(message_qry)

        return message_qry.all()




api.add_resource(TopicList, "/topics")
api.add_resource(Topic, "/topics/<int:topic_id>")
api.add_resource(PostList, "/topics/<int:topic_id>/posts")

api.add_resource(AlbumList, "/albums")
api.add_resource(Album, "/albums/<int:album_id>")
api.add_resource(PictureList, "/albums/<int:album_id>/pictures")

api.add_resource(MessageList, "/messages")
api.add_resource(MessageList, "/messages/folder/<folder_id>")

if __name__ == '__main__':
    #user_ressources.debug = True
    app.debug = True
    app.run("0.0.0.0")
