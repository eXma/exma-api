import hashlib
from datetime import datetime, timedelta, MAXYEAR
import phpserialize
import sys


__all__ = ["ForumPermissions", "UserBan", "ApiUser", "exma_passhash"]

GUEST_MASK = [2]


class ForumPermissions(object):
    """This class handles the forum permissions.

    """
    PERM_READ = "read_perms"
    PERM_REPLY = 'reply_perms'
    PERM_START = 'start_perms'
    PERM_UPLOAD = 'upload_perms'
    PERM_SHOW = 'show_perms'

    def __init__(self, permission_array):
        """Initialize the permission object by parsing a permission string.

        :type permission_array: str or unicode
        :param permission_array: The phpserializes crippled arraystring
        """
        self._permissions = parse_permissions(permission_array)

    def is_fulfilled(self, mask_tuple, permission_type):
        """This checks if one of the given masks are contained in the perms.

        :type mask_tuple: tuple or list
        :param mask_tuple: The set of the permissions to check
        :type permission_type: str
        :param permission_type: The permission type to check
        :rtype: bool
        :return: True if one of the permission matches, False otherwise.
        """
        perms = self._permissions.get(permission_type)
        if perms is not None:
            for mask in mask_tuple:
                if mask in perms:
                    return True
        return False


def parse_permissions(permission_array):
    """Parses a python dict of lists from the forum permission array.

    The forum permissions are very creative saved in the database. Its a
    php-serialized associative array that holds the different permission
    mask ids as string-value for the permission type key. The single ids
    are separated by commas.

    This function parses this to a dict with the permission types as keys
    and a list of the mask ids as value.

    :type permission_array: str or bytes
    :param permission_array: The phpserializes crippled arraystring
    :rtype: dict[str, set[bytes]]
    :return: The parsed dict with the permissions.
    """
    parsed = {}
    if not len(permission_array):
        return parsed

    if isinstance(permission_array, str):
        permission_array = bytes(permission_array, "utf8")
    perms = phpserialize.loads(permission_array, decode_strings=True)
    for perm_type in perms:
        parsed[perm_type] = set()
        if perms[perm_type] is not None:
            for mask in perms[perm_type].split(","):
                try:
                    parsed[perm_type].add(int(mask))
                except ValueError:
                    pass
    return parsed


def exma_passhash(password, salt):
    """Generate a ipb-compatible password hash.

    The passwords from the ipb are salted and triple md5'ed (because doing
    rot13 twice is more secure!). It can be seen as:
    >> md5( md5(salt) + md5(password) )
    For md5() functions that kake a str or unicode and get the result in
    hex representation back.

    :param password: The plain password.
    :type password: str or unicode
    :param salt: The plain salt.
    :type salt: str or unicode
    :return: The salted hash.
    :rtype: str
    """
    password_hash = hashlib.md5(password.encode("latin1")).hexdigest()
    salt_hash = hashlib.md5(salt.encode("latin1")).hexdigest()
    return hashlib.md5((salt_hash + password_hash).encode("ascii")).hexdigest()


class UserBan(object):
    def __init__(self, start, end, duration):
        """Creates an instance.

        :type start: datetime.datetime
        :param start: The start of the Ban.
        :type end: datetime.datetime
        :param end: The end of the Ban.
        :type duration: datetime.timedelta
        :param duration: The duration of the Ban.
        """
        self.start = start
        self.end = end
        self.duration = duration

    def is_active(self):
        """Tells if the ban is currently active.

        :rtype: bool
        :return: True if active, false else.
        """
        return self.start < datetime.now() < self.end

    @staticmethod
    def from_banline(db_temp_ban):
        """Parses a user temp_ban line from the db and create a UserBan instance

        A banline is a string of four parts separated by a colon.
        The first part is the start of the ban, encoded as unix
        epoch timestamp. The second is the end of the ban, also
        encoded as unix epoch timestamp. The third is the duration
        of the ban. The duration are either hours or days. The unit
        is told by the fourth part, which is either a "h" for hour
        or a "d" for days.

        I don't know which diseased mind thought this would be a
        good format...

        :type db_temp_ban: str or unicode
        :param db_temp_ban:
        :rtype: UserBan or None
        :return: A UserBan instance or None if the line was not set/malformed
        """
        if db_temp_ban is not None and str(db_temp_ban) != "0":
            ban_parts = db_temp_ban.split(":")
            if len(ban_parts) == 4:
                try:
                    start = datetime.fromtimestamp(int(ban_parts[0]))
                    if float(ban_parts[1]) < sys.maxsize:
                        end = datetime.fromtimestamp(int(ban_parts[1]))
                        duration_hours = ban_parts[2]
                        if ban_parts[3] == "d":
                            duration_hours *= 24
                        duration = timedelta(hours=duration_hours)
                    else:
                        end = datetime(year=MAXYEAR, day=31, month=12)
                        duration = end - start
                    return UserBan(start, end, duration)
                except ValueError:
                    pass
        return None


class ApiUser(object):
    """A dummy mixin to implement anonymous users.
    """

    def authenticated(self):
        """tells if the user is authentiated.

        :return: False for this implementation
        """
        return False

    @property
    def perm_masks(self):
        """Get the permission masks the user have.

        :rtype: list
        :return: A List of the masks.
        """
        return GUEST_MASK