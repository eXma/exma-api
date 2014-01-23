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


class EventCategory(object):
    _event_categories = {}
    _category_tags = {}

    def __init__(self, category_id, tag, name):
        """Initialize a category object.

        :param category_id: The id of the category.
        :type category_id: int
        :param tag: The tag of the category.
        :type tag: str
        :param name: The name of the category.
        :type name: str
        """
        self.id = category_id
        self.tag = tag
        self.name = name

    @classmethod
    def by_id(cls, category_id):
        if category_id in cls._event_categories:
            return cls._event_categories[category_id]
        return cls._unknown()

    @classmethod
    def by_tag(cls, tag):
        if tag in cls._category_tags:
            category_id = cls._category_tags[tag]
            if category_id in cls._event_categories:
                return cls._event_categories[category_id]
        return cls._unknown()

    @staticmethod
    def _unknown():
        return EventCategory(-1, "unknown", "(UNBEKANNT)")

    @classmethod
    def make(cls, category_id, tag, name):
        cls._event_categories[category_id] = EventCategory(category_id, tag, name)
        cls._category_tags[tag] = category_id

    @classmethod
    def all_categories(cls):
        categories = cls._event_categories.values()
        return sorted(categories, key=lambda x: x.id)


EventCategory.make(0, "none", "Keine", )
EventCategory.make(1, "party", "Party", )
EventCategory.make(2, "culture", "Kunst oder Kultur", )
EventCategory.make(3, "club", "Kneipe oder Club", )
EventCategory.make(4, "relax", "Freizeit oder Erholung", )
EventCategory.make(5, "studentclub", "Studentenclubs", )
EventCategory.make(6, "studentday", "Dresdner Studententage", )
EventCategory.make(7, "science", "Forschung und Wissen")


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
