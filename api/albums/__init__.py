from api.albums.ressources import AlbumList, Album, PictureList
from api.request_helper import charset_fix_decorator
from flask import Blueprint
import flask_restful


def album_blueprint():
    album_bp = Blueprint("albums", __name__)

    album_api = flask_restful.Api(decorators=[charset_fix_decorator])
    album_api.init_app(album_bp)

    album_api.add_resource(AlbumList, "/")
    album_api.add_resource(Album, "/<int:album_id>")
    album_api.add_resource(PictureList, "/<int:album_id>/pictures")

    return album_bp