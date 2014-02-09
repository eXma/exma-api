def make_blueprint():
    from api.users.blueprint import user_blueprint

    return user_blueprint()