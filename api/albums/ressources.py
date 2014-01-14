from api.albums import fieldsets
from api.request_helper import limit_query
from api.users import authorization
from flask.ext.restful import marshal_with, abort
from flask.ext.restful_fieldsets import marshal_with_fieldset
from flask.ext import restful

import db_backend
from db_backend.config import connection


class AlbumList(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.AlbumFields)
    def get(self):
        albums_qry = connection.session.query(db_backend.DbPixAlbums).order_by(db_backend.DbPixAlbums.time.desc())
        albums_qry = limit_query(albums_qry)

        return albums_qry.all()


class Album(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.AlbumFields)
    def get(self, album_id):
        album = db_backend.DbPixAlbums.by_id(album_id)
        if album is None:
            return abort(404, message="Album not found")
        return album


class PictureList(restful.Resource):
    @authorization.require_login
    @marshal_with_fieldset(fieldsets.PictureFields)
    def get(self, album_id):
        album = db_backend.DbPixAlbums.by_id(album_id)
        if album is None:
            abort(404, message="album not found")

        return album.pictures