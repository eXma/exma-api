import datetime
import db_backend


_event_duration = datetime.timedelta(hours=6)


def make_event_instances(db_event, start, end):
    """Create all event instances between the given interval

    :param db_event: The database event
    :type db_event: db_backend.DbEvents
    :param start: The start date (including)
    :type start: datetime.datetime
    :param end: The end date (including)
    :type end: datetime.datetime
    :return The list if instances for the event.
    :rtype: list of EventInstance
    """
    instances = []
    for date_instance in db_event.recurrence_rule.between(start, end, True):
        instances.append(EventInstance(date_instance, db_event))

    return instances


class EventInstance(object):
    """This is a wrapper of the DbEvents for a specific recurred
    instance of the event.
    """

    def __init__(self, date_instance, db_instance):
        """Create the specific event instance

        :type date_instance: datetime.datetime
        :param date_instance: The start date of this specific instance
        :type db_instance: db_backend.DbEvents
        :param db_instance: The real instance of the event
        """
        self.date_instance = date_instance
        self.db_instance = db_instance
        self.editable = False
        self.allDay = False

    @property
    def start(self):
        """Get the start date of this specific instance

        :rtype: datetime.datetime
        :return: The start date
        """
        return self.date_instance

    @property
    def end(self):
        """Get the end date of this specific instance.

        :rtype: datetime.datetime
        :return: The end date.
        """
        return self.date_instance + _event_duration

    @property
    def title(self):
        return self.db_instance.topic.title

    def __getattr__(self, item):
        return getattr(self.db_instance, item)
