from flask.ext.restful import reqparse
from functools import wraps


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


def charset_fix_decorator(response_func):
    """Fix the output mime-type by adding the charset information.
    """

    @wraps(response_func)
    def wrapper(*args, **kwargs):
        response = response_func(*args, **kwargs)
        if "charset" not in response.headers['Content-Type']:
            response.headers['Content-Type'] += "; charset=UTF-8"
        return response

    return wrapper