import phpserialize

__author__ = 'jan'

GUEST_MASK = [2]

class ForumPermissions(object):
    """This class handles the forum permissions.

    """
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

    :type permission_array: str or unicode
    :param permission_array: The phpserializes crippled arraystring
    :rtype: dict of list
    :return: The parsed dict with the permissions.
    """
    parsed = {}
    perms = phpserialize.loads(permission_array)
    for perm_type in perms:
        parsed[perm_type] = set()
        if perms[perm_type] is not None:
            for mask in perms[perm_type].split(","):
                try:
                    parsed[perm_type].add(int(mask))
                except ValueError:
                    pass
    return parsed

