from sqlalchemy import create_engine, MetaData, Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.sql import ColumnCollection
import os

import user


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
    except Exception as e:
        pass
    return pw

pw_file = os.path.join(os.path.dirname(__file__), "..", "exma_pw")

Base = declarative_base()
engine = create_engine('mysql://%s@127.0.0.1/exma?charset=utf8' % get_passwd(pw_file))
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


class DbMembers(Base, user.ApiUser):
    """This handles the ipb_members data within the exma ipb database
    """
    props = ColumnCollection(Column('id', Integer, primary_key=True))
    __table__ = Table('ipb_members', meta, *props, autoload=True)

    converge = relationship("DbMembersConverge", uselist=False)

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
        return session.query(DbMembers).filter_by(name=username).first()

    @staticmethod
    def by_id(user_id):
        """Get a user by its id

        :type user_id: int
        :param user_id: The id of the user.
        :rtype: DbMembers or None
        :return: The found User or None.
        """
        return session.query(DbMembers).filter_by(id=user_id).first()

    def authenticated(self):
        """Tells if the user was authenticated.

        :rtype: bool
        :return: True if so.
        """
        return not self.is_banned()


class DbMembersConverge(Base):
    """Holds the password hash & salt (table ipb_members_converge)
    """
    props = ColumnCollection(Column('converge_id', Integer, ForeignKey("ipb_members.id"), primary_key=True))
    __table__ = Table('ipb_members_converge', meta, *props, autoload=True)

