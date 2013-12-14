from api.user import authorization
import db_backend
from flask import Blueprint, send_file, send_from_directory
from flask.ext.restful import abort

import os
from pixma_images import thumbnailer
from db_backend.config import connection

_pixma_bp = Blueprint("pixma", __name__)


def pixma_blueprint():
    return _pixma_bp


@_pixma_bp.route("/<int:pic_id>.jpg", defaults={"type_string": None})
@_pixma_bp.route("/<int:pic_id>_<string:type_string>.jpg")
@authorization.require_login
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
        connection.session.commit()

    filepath = os.path.join("/mnt/tmp", filename)
    if not os.path.isfile(filepath):
        abort(404)

    if type_string == "sq":
        handle = thumbnailer.load_square_resized(filepath)
        return send_file(handle, mimetype="image/jpeg")

    return send_from_directory("/mnt/tmp", filename)
