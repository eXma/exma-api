from api.events.request_parsing import EventInterval, _resolve_category
from api.users import authorization
from api.events import fieldsets
from flask.ext import restful

from db_backend import mapping
from db_backend.mapping.config import connection
from db_backend.utils.events import EventCategory
from flask.ext.restful import abort
from flask.ext.restful_fieldsets import marshal_with_fieldset
from sqlalchemy.orm import joinedload


class EventList(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventFields)
    @_resolve_category
    def get(self, category=None):
        interval = EventInterval()
        print("%s, %s" % (interval.start, interval.end))

        event_qry = mapping.DbEvents.query_between(interval.start,
                                                   interval.end)
        event_qry = event_qry.options(joinedload(mapping.DbEvents.topic).joinedload(mapping.DbTopics.forum))
        event_qry = event_qry.options(joinedload(mapping.DbEvents.location))
        if category is not None:
            event_qry = event_qry.filter(mapping.DbEvents.category == category.id)

        event_list = []
        for event in event_qry:
            if not event.topic.forum.can_read(authorization.current_user.perm_masks):
                continue
            event_list.extend(event.instances_between(interval.start,
                                                      interval.end))

        return event_list


class EventCategoryList(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventCategoryFields)
    def get(self):
        return EventCategory.all_categories()


class Event(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventFields)
    def get(self, event_id):
        event = mapping.DbEvents.by_id(event_id, authorization.current_user.perm_masks)
        if event is None:
            abort(404, message="Event not found")
        event_instance = event.first_instance()
        if event_instance is None:
            abort(404, message="No event instance found")
        return event_instance


class LocationList(restful.Resource):
    @marshal_with_fieldset(fieldsets.EventLocationFields)
    def get(self):
        location_qry = connection.session.query(mapping.DbLocations)
        return location_qry.all()


class Location(restful.Resource):
    pass


class OrganizerList(restful.Resource):
    pass


class Organizer(restful.Resource):
    pass