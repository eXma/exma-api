def make_blueprint():
    from api.albums.blueprint import album_blueprint

    return album_blueprint()