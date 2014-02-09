from api.albums import fieldsets
from api.request_helper import limit_query
from api.users import authorization
from flask.ext.restful import abort
from flask.ext.restful_fieldsets import marshal_with_fieldset
from flask.ext import restful

from db_backend import mapping
from db_backend.mapping.config import connection


class AlbumList(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.AlbumFields)
    def get(self):
        albums_qry = connection.session.query(mapping.DbPixAlbums).order_by(mapping.DbPixAlbums.time.desc())
        albums_qry = limit_query(albums_qry)

        return albums_qry.all()


class Album(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.AlbumFields)
    def get(self, album_id):
        album = mapping.DbPixAlbums.by_id(album_id)
        if album is None:
            return abort(404, message="Album not found")
        return album


class PictureList(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.PictureFields)
    def get(self, album_id):
        album = mapping.DbPixAlbums.by_id(album_id)
        if album is None:
            abort(404, message="album not found")

        return album.pictures