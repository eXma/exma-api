from flask.ext.restful import fields

topic_fields = {
    'tid': fields.Integer,
    'title': fields.String,
    'last_post': fields.String,
    'last_poster_name': fields.String,
    'starter_name': fields.String
}

post_fields = {
    'pid': fields.Integer,
    'post': fields.String,
    'author_name': fields.String,
    'post_date': fields.String,
}