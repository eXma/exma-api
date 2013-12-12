from api.messages import fieldsets
from api.request_helper import limit_query
from api.user import authorization
from flask.ext.restful import marshal_with, abort, reqparse
from flask.ext import restful
from sqlalchemy.orm import joinedload

import db_backend


class MessageList(restful.Resource):
    @authorization.require_login
    @marshal_with(fieldsets.message_fields)
    def get(self, folder_id=None):

        parser = reqparse.RequestParser()
        parser.add_argument('since', type=int)
        parser.add_argument('before', type=int)
        parser.add_argument('bodies', type=bool)
        req_args = parser.parse_args()

        message_qry = db_backend.DbMessageTopics.for_user(authorization.current_user).order_by(
            db_backend.DbMessageTopics.mt_date.desc())

        if req_args.get("bodies") is not None:
            message_qry = message_qry.options(joinedload('body'))

        if req_args.get("since") is not None:
            message_qry = message_qry.filter(db_backend.DbMessageTopics.mt_id > req_args["since"])
        if req_args.get("before") is not None:
            message_qry = message_qry.filter(db_backend.DbMessageTopics.mt_id > req_args["before"])

        if folder_id is not None:
            message_qry = message_qry.filter_by(mt_vid_folder=folder_id)
        message_qry = limit_query(message_qry)

        return message_qry.all()


class FolderList(restful.Resource):
    @authorization.require_login
    @marshal_with(fieldsets.folder_fields)
    def get(self):
        dir_list = authorization.current_user.extra.virtual_dirs()
        return dir_list.as_list


class Message(restful.Resource):
    @authorization.require_login
    @marshal_with(fieldsets.message_fields)
    def get(self, message_topic_id):
        message_qry = db_backend.DbMessageTopics.for_user(authorization.current_user, message_topic_id)
        message_qry = message_qry.options(joinedload('body'))
        message = message_qry.first()
        if message is None:
            abort(404, message="Message not found for user")

        return message
