from sqlalchemy import create_engine, MetaData, Table, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import ColumnCollection
import phpserialize

import user

__author__ = 'jan'

def get_passwd(filename):
    """Read the username/passwd from an extra file.

    This is to prevent the password from being committed to the VCS.

    :param filename: The name of the file where the pw is stored.
    :return: The username:password
    """
    pw = ""
    try:
        with open(filename, "r") as f:
            pw = f.read()
    except :
        pass
    return pw


Base = declarative_base()
engine = create_engine('mysql://%s@127.0.0.1/exma?charset=utf8' % get_passwd("exma_pw"))
meta = MetaData(bind=engine)
#session = None
session = scoped_session(sessionmaker(bind=engine))


class DbTopics(Base):
    """This handles the ipb_topics data within the exma ipb database
    """
    __table__ = Table('ipb_topics', meta, autoload=True)


class DbForums(Base):
    """This handles the ipb_forum data within the exma ipb database.
    """

    props = ColumnCollection(Column('id', Integer, primary_key=True))
    __table__ = Table('ipb_forums', meta, *props, autoload=True)

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
        return self.perms.is_fulfilled(user_mask_tuple, "read_perms")

    @staticmethod
    def guest_readable():
        """Get a list of all db forums that are readable fur guests.

        :rtype: list of DbForums
        :return: The list of fetched forum objects.
        """
        forums = []
        for forum in session.query(DbForums):
            if forum.can_read(user.GUEST_MASK):
                forums.append(forum)

        return forums