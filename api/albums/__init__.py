from api.albums.ressources import AlbumList, Album, PictureList
from api.messages.ressources import MessageList, Message, FolderList
from flask import Blueprint
import flask_restful


def album_blueprint():
    album_bp = Blueprint("albums", __name__)

    album_api = flask_restful.Api()
    album_api.init_app(album_bp)

    album_api.add_resource(AlbumList, "/")
    album_api.add_resource(Album, "/<int:album_id>")
    album_api.add_resource(PictureList, "/<int:album_id>/pictures")

    return album_bp