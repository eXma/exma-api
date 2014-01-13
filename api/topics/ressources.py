from api.request_helper import limit_query
from api.topics import fieldsets
from api.users import authorization
from flask.ext.restful import abort
from flask.ext.restful_fieldsets import marshall_with_fieldset
from flask.ext import restful

import db_backend
from db_backend.config import connection


class TopicList(restful.Resource):
    @marshall_with_fieldset(fieldsets.TopicFields)
    def get(self, forum_id=None):
        guest_forums = db_backend.DbForums.guest_readable()
        guest_forum_ids = [f.id for f in guest_forums]

        topic_qry = connection.session.query(db_backend.DbTopics).filter(
            db_backend.DbTopics.forum_id.in_(guest_forum_ids)).filter_by(approved=1).order_by(
            db_backend.DbTopics.last_post.desc()).limit(100)
        topic_qry = limit_query(topic_qry)

        topics = topic_qry.all()

        return topics


class PostList(restful.Resource):
    @marshall_with_fieldset(fieldsets.PostFields)
    def get(self, topic_id):
        topic = db_backend.DbTopics.by_id(topic_id, authorization.current_user.perm_masks)
        if topic is None:
            abort(404, message="No topic with this id available")

        posts = db_backend.DbPosts.by_topic_query(topic_id).limit(40)
        return posts.all()


class Topic(restful.Resource):
    @marshall_with_fieldset(fieldsets.TopicFields)
    def get(self, topic_id=None):
        topic = db_backend.DbTopics.by_id(topic_id, authorization.current_user.perm_masks)
        if topic is None:
            abort(404, message="No topic with this id available")
        return topic