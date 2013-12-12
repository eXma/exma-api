from flask.ext.restful import reqparse


def limit_query(query):
    """Apply the limit/offset querystring args.

    :param query: The query to limit.
    :type query: sqlalchemy.orm.query.Query
    :return: The limited query.
    :rtype : sqlalchemy.orm.query.Query
    """

    parser = reqparse.RequestParser()
    parser.add_argument('limit', type=int)
    parser.add_argument('offset', type=int)
    req_args = parser.parse_args()

    limit = req_args.get("limit")
    offset = req_args.get("offset")
    if limit is not None and limit > 0:
        query = query.limit(limit)
    if offset is not None and offset > 0:
        query = query.offset(offset)
    return query
