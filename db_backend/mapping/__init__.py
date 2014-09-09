import datetime

from dateutil import rrule
from db_backend.mapping.config import connection
from db_backend.utils.events import make_event_instances, EventCategory
from sqlalchemy import Table, Column, Integer, ForeignKey, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, joinedload
from db_backend.utils.message import DirList
from db_backend.utils import user, timestamps



# ToDo: Refactor this in smaller modules
# ToDo: Use any sort of DI to give a fake database for unittests


Base = declarative_base()


def auto_table(name, *cols):
    return Table(name, connection.metadata, *cols, autoload=True)


class DbTopics(Base):
    """This handles the ipb_topics data within the exma ipb database
    """
    __table__ = auto_table('ipb_topics',
                           Column('tid', Integer, primary_key=True),
                           Column('forum_id', Integer, ForeignKey("ipb_forums.id")))

    forum = relationship("DbForums", uselist=False)
    all_posts = relationship("DbPosts", backref=backref('topic'))

    @staticmethod
    def by_id(topic_id, user_mask_tuple):
        """Get a topic by its topic id.

        :type topic_id: int
        :param topic_id: The id to query for.
        :type user_mask_tuple: list or tuple
        :param user_mask_tuple: A set of user masks that are checked for read-access of the forum containing the topic..
        :rtype: DbTopics or None
        :return: The DbTopics instance or None if none exists or read is not granted for the given mask.
        """
        topic = connection.session.query(DbTopics).filter_by(tid=topic_id).filter_by(approved=1).first()
        if topic is not None:
            if topic.forum.can_read(user_mask_tuple):
                return topic
        return None


class DbForums(Base):
    """This handles the ipb_forum data within the exma ipb database.
    """

    __table__ = auto_table('ipb_forums',
                           Column('id', Integer, primary_key=True))

    @property
    def perms(self):
        """Get the ForumPermissions object for this forum.

        :rtype: ForumPermissions
        :return: The instance.
        """
        if not hasattr(self, "_perms"):
            self._perms = user.ForumPermissions(self.permission_array)
        return self._perms

    def can_read(self, user_mask_tuple):
        """Checks if the forum can be readed by one of the given permission masks.

        :type user_mask_tuple: list of int
        :param user_mask_tuple: A tuple of permission masks to check.
        :rtype: bool
        :return: True if read is granted.
        """
        return self.perms.is_fulfilled(user_mask_tuple, user.ForumPermissions.PERM_READ)

    @staticmethod
    def readable_by(user_mask_set):
        """Get a list of all db forums that are readable for the given mask.

        :param user_mask_set: A collection of permission masks
        :type user_mask_set: set of int
        :rtype: list of DbForums
        :return: The list of fetched forum objects.
        """
        forums = []
        for forum in connection.session.query(DbForums):
            if forum.can_read(user_mask_set):
                forums.append(forum)
        return forums

    @staticmethod
    def guest_readable():
        """Get a list of all db forums that are readable fur guests.

        :rtype: list of DbForums
        :return: The list of fetched forum objects.
        """
        forums = []
        for forum in connection.session.query(DbForums):
            if forum.can_read(user.GUEST_MASK):
                forums.append(forum)

        return forums


class DbPosts(Base):
    """Handle the post data from the database (table: ipb_posts).
    """
    __table__ = auto_table('ipb_posts',
                           Column('pid', Integer, primary_key=True),
                           Column('topic_id', Integer, ForeignKey("ipb_topics.tid")))

    @staticmethod
    def by_topic_query(topic_id):
        """Fetches a queryset with all posts for the given topic id.

        :param topic_id: The topic id to query posts for.
        :type topic_id: int
        :return: A DbPosts queryset for this topic id or None if not existent.
        :rtype: sqlalchemy.orm.query.Query
        """
        return connection.session.query(DbPosts).filter_by(topic_id=topic_id).order_by(
            DbPosts.post_date.desc()).filter_by(queued=0)


class DbEvents(Base):
    """Handle the events data in the database (table: exma_events).
    """
    __table__ = auto_table('exma_events',
                           Column('event_id', Integer, ForeignKey("ipb_topics.tid"), primary_key=True),
                           Column('location_id', Integer, ForeignKey("exma_locations.lid")))

    topic = relationship("DbTopics", uselist=False)
    location = relationship("DbLocations", uselist=False)


    @staticmethod
    def by_id(event_id, user_mask_tuple):
        """Get the event for the given event id if user_mask is ok

        :param event_id: The id of the event
        :type event_id: int
        :param user_mask_tuple: The mask of the current user
        :type user_mask_tuple: list or tuple
        :return: Teh event for this id or None
        :rtype: DbEvents or None
        """
        event = connection.session.query(DbEvents) \
            .filter_by(event_id=event_id) \
            .options(joinedload(DbEvents.topic)) \
            .options(joinedload(DbEvents.location)) \
            .join(DbEvents.topic) \
            .filter_by(approved=1).first()
        if event is not None:
            if event.topic.forum.can_read(user_mask_tuple):
                return event
        return None


    @property
    def category_instance(self):
        """Get  the category of the event.

        :rtype: EventCategory
        :return: The Category
        """
        return EventCategory.by_id(self.category)

    @property
    def start_date(self):
        return timestamps.from_db(self.start)

    @property
    def end_date(self):
        return timestamps(self.end)

    @property
    def recurrence_interval(self):
        if self.type == 0:
            return rrule.DAILY
        else:
            return rrule.WEEKLY

    @property
    def type_name(self):
        if self.type != 0:
            return "WEEKLY"
        elif self.end_date - self.start_date < datetime.timedelta(days=1):
            return "SINGLE"
        else:
            return "DAYLY"

    @property
    def recurrence_rule(self):
        """Get the rrule for this event

        :rtype: rrule.rrule
        :return:
        """
        return rrule.rrule(self.recurrence_interval,
                           dtstart=self.start_date,
                           until=self.end_date)

    def instances_between(self, start, end):
        return make_event_instances(self, start, end)

    def first_instance(self, reference=None):
        if reference is None:
            reference = self.start_date
        instance = make_event_instances(self, reference, reference)
        if len(instance):
            return instance[0]
        return None


    @classmethod
    def query_between(cls, start, end):
        """Create a query between the given dates.

        :param start: The start timestamp (inclusive)
        :type start: datetime.datetime
        :param end: The end timestamp (exclusive)
        :type end: datetime.datetime
        :return: A queryset between the given dates
        :rtype: sqlalchemy.orm.query.Query
        """
        start_timestamp = int(start.timestamp())
        end_timestamp = int(end.timestamp())
        qry = connection.session.query(DbEvents).filter(
            or_(and_(DbEvents.start >= start_timestamp,
                     DbEvents.start < end_timestamp),
                and_(DbEvents.end >= start_timestamp,
                     DbEvents.end < end_timestamp),
                and_(DbEvents.start < start_timestamp,
                     DbEvents.end > end_timestamp)))
        return qry


class DbLocations(Base):
    """Handle the location data for the events from the database (table: exma_locations).
    """
    __table__ = auto_table('exma_locations',
                           Column('lid', Integer, primary_key=True))

    @classmethod
    def by_id(cls, location_id):
        return connection.session.query(DbLocations).filter_by(lid=location_id).first()


class DbOrganizers(Base):
    """Handles the organizers of events
    """
    __table__ = auto_table('exma_veranstalter',
                           Column('vid', Integer, primary_key=True),
                           Column('location_id', Integer, ForeignKey('exma_locations.lid')),
                           Column('mid', Integer, ForeignKey('ipb_members.id')))

    location = relationship("DbLocations", uselist=False)
    member = relationship("DbMembers", uselist=False)

    @classmethod
    def by_id(cls, organizer_id):
        return connection.session.query(DbOrganizers).filter_by(vid=organizer_id).first()


class DbPixAlbums(Base):
    __table__ = auto_table('pixma_album',
                           Column('a_id', Integer, primary_key=True),
                           Column('l_id', Integer, ForeignKey("exma_locations.lid")),
                           Column('thumb_id', Integer, ForeignKey('pixma_pics.pid')))

    location = relationship("DbLocations", uselist=False)
    thumbnail = relationship("DbPixPics", uselist=False, foreign_keys="DbPixAlbums.thumb_id", lazy="joined")

    @staticmethod
    def by_id(album_id):
        return connection.session.query(DbPixAlbums).filter_by(a_id=album_id).first()


class DbPixComments(Base):
    __table__ = auto_table('pixma_comments',
                           Column('msg_id', Integer, primary_key=True),
                           Column('picture_id', Integer, ForeignKey("pixma_pics.pid")),
                           Column('user_id', Integer, ForeignKey('ipb_members.id')))

    picture = relationship("DbPixPics")
    member = relationship("DbMembers")


class DbPixPeople(Base):
    __table__ = auto_table('pixma_people',
                           Column('user', Integer, ForeignKey('ipb_members.id'), primary_key=True),
                           Column('picture_id', Integer, ForeignKey("pixma_pics.pid"), primary_key=True),
                           Column('album_id', Integer, ForeignKey('pixma_album.a_id')))

    member = relationship("DbMembers")
    picture = relationship("DbPixPics")
    album = relationship("DbPixAlbums")


class DbPixPics(Base):
    __table__ = auto_table('pixma_pics',
                           Column('pid', Integer, primary_key=True),
                           Column('aid', Integer, ForeignKey('pixma_album.a_id')))

    album = relationship("DbPixAlbums", backref=backref("pictures"), foreign_keys="DbPixPics.aid")

    @staticmethod
    def by_id(pic_id):
        return connection.session.query(DbPixPics).filter_by(pid=pic_id).first()


class DbMessageTopics(Base):
    """This is a message topic from the ipb database. The table is ipb_message_topics.

    Messages within the ipb are a strange thing. The message-body itself exists only
    once within the database. If the message is send teh body is created and two of
    this topics referencing the body. One topic is "owned" by the autor and placed in
    its "Sent" mailbox, The other is "owned" by the recipient and placed in its "Inbox".

    If you want to get all messages a user can see then ignore the message bodies and
    fetch all topics that are "owned" by the user. These are the ones that should be
    visible to the user.The from/to/author does not matter for this. For example a user
    can delete a message from its "Send" folder, This means only its topic will be
    deleted. The body and the title for the recipient stay alive and can be found.
    """
    __table__ = auto_table('ipb_message_topics',
                           Column('mt_id', Integer, primary_key=True),
                           Column('mt_from_id', Integer, ForeignKey('ipb_members.id')),
                           Column('mt_to_id', Integer, ForeignKey('ipb_members.id')),
                           Column('mt_owner_id', Integer, ForeignKey('ipb_members.id')),
                           Column('mt_msg_id', Integer, ForeignKey('ipb_message_text.msg_id')))

    body = relationship("DbMessageText", backref=backref("headers"))

    owner = relationship("DbMembers", backref=backref("owned_messages"), foreign_keys="DbMessageTopics.mt_owner_id",
                         lazy="joined")
    from_user = relationship("DbMembers", foreign_keys="DbMessageTopics.mt_from_id", lazy="joined")
    to_user = relationship("DbMembers", foreign_keys="DbMessageTopics.mt_to_id", lazy="joined")

    @staticmethod
    def for_user(user, topic_id=None):
        """Return a queryset of all Messages or a single message owned by a specific user.

        :type user: DbMembers
        :param user: Teh user to select the messages for.
        :type topic_id: int
        :param topic_id: optional a topic id to get a single message topic.
        :rtype: sqlalchemy.orm.query.Query
        :return: The query.
        """
        qry = connection.session.query(DbMessageTopics).filter(DbMessageTopics.owner == user)
        if topic_id is not None:
            qry = qry.filter_by(mt_id=topic_id)
        return qry


class DbMessageText(Base):
    """Hold the real message bodies of the users messages. Table is ipb_message_text.

    See DbMessageTopics for more information on the text/topic relationship.
    """
    __table__ = auto_table('ipb_message_text',
                           Column('msg_id', Integer, primary_key=True),
                           Column('msg_author_id', Integer, ForeignKey('ipb_members.id')))

    author = relationship("DbMembers")


class DbGroups(Base):
    __table__ = auto_table('ipb_groups',
                           Column('g_id', Integer, primary_key=True))


    @property
    def permission_masks(self):
        return _split_set(self.g_perm_id)


def _split_set(raw_value):
    return set([int(item) for item in raw_value.split(",") if len(item)])


class DbMembers(Base, user.ApiUser):
    """This handles the ipb_members data within the exma ipb database
    """
    __table__ = auto_table('ipb_members',
                           Column('id', Integer, primary_key=True),
                           Column('mgroup', Integer, ForeignKey("ipb_groups.g_id")))

    converge = relationship("DbMembersConverge", uselist=False)
    extra = relationship("DbMembersExtra", uselist=False)
    primary_group = relationship("DbGroups", uselist=False)

    @property
    def secondary_group_ids(self):
        return _split_set(self.mgroup_others)

    @property
    def group_permissions(self):
        """Get all permission masks that the user have from its group memberships

        :rtype: set of int
        :return: A set of group permission masks
        """
        result = self.primary_group.permission_masks
        if len(self.secondary_group_ids) > 0:
            qry = connection.session.query(DbGroups.g_perm_id.label("perm")) \
                .filter(DbGroups.g_id.in_(self.secondary_group_ids))
            for group_perms in qry:
                result.update(_split_set(group_perms.perm))
        return result

    def password_valid(self, password):
        """Check if a given password is the password of the user.

        :type password: str or unicode
        :param password: The password to check.
        :rtype: bool
        :return: True if the password is correct.
        """
        reference_hash = self.converge.converge_pass_hash
        if reference_hash is not None:
            salt = self.converge.converge_pass_salt
            hash = user.exma_passhash(password, salt)
            return hash == reference_hash
        return False

    @property
    def ban(self):
        """Get the parsed UserBan object or None if none.

        :rtype: UserBan or None
        :return: The instance or None
        """
        if not hasattr(self, "_ban"):
            self._ban = user.UserBan.from_banline(self.temp_ban)
        return self._ban

    def is_banned(self):
        """Tells if the user is currently banned.

        :rtype: bool
        :return: True if banned
        """
        return self.ban is not None and self.ban.is_active()

    @staticmethod
    def by_name(username):
        """Get a user by its username

        :type username: str or unicode
        :param username: The username to search for.
        :rtype: DbMembers or None
        :return: The found User or None.
        """
        return connection.session.query(DbMembers).filter_by(name=username).first()

    @staticmethod
    def by_id(user_id):
        """Get a user by its id

        :type user_id: int
        :param user_id: The id of the user.
        :rtype: DbMembers or None
        :return: The found User or None.
        """
        return connection.session.query(DbMembers).filter_by(id=user_id).first()

    def authenticated(self):
        """Tells if the user was authenticated.

        :rtype: bool
        :return: True if so.
        """
        return not self.is_banned()

    @property
    def perm_masks(self):
        return self.group_permissions


class DbMembersConverge(Base):
    """Holds the password hash & salt (table ipb_members_converge)
    """
    __table__ = auto_table('ipb_members_converge',
                           Column('converge_id', Integer, ForeignKey("ipb_members.id"), primary_key=True))


class DbMembersExtra(Base):
    __table__ = auto_table('ipb_member_extra',
                           Column('id', Integer, ForeignKey("ipb_members.id"), primary_key=True))

    def virtual_dirs(self):
        """Get a wrapper for the virtual message dirs of the user

        :rtype: db_backend.message.DirList
        :return: The Dirlist
        """
        if hasattr(self, "_vdirs"):
            return getattr(self, "_vdirs")
        self._vdirs = DirList(self)
        return self._vdirs