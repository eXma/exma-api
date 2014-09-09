from datetime import MAXYEAR, timedelta
import unittest
from db_backend.utils import timestamps
from db_backend.utils.user import exma_passhash, ApiUser, GUEST_MASK, parse_permissions, ForumPermissions, UserBan


class TestPasswordHandling(unittest.TestCase):
    def test_0010_valid_password(self):
        hash = exma_passhash("test", "abc")
        self.assertEqual(hash, '57378fa5f7f15da155244b48622b2749')

    def test_0020_invalid_password(self):
        hash = exma_passhash("peng", "abc")
        self.assertNotEqual(hash, '57378fa5f7f15da155244b48622b2749')

    def test_0030_invalid_salt(self):
        hash = exma_passhash("test", "peng")
        self.assertNotEqual(hash, '57378fa5f7f15da155244b48622b2749')


class TestApiUser(unittest.TestCase):
    def test_0010_dummy_user_unauthenticated(self):
        user = ApiUser()
        self.assertFalse(user.authenticated())

    def test_0020_dummy_user_is_guest(self):
        user = ApiUser()
        self.assertEqual(user.perm_masks, GUEST_MASK)


class TestParsePermissions(unittest.TestCase):
    parsed_ref = {'start_perms': {3, 4, 9, 11, 12, 15, 16, 18},
                  'upload_perms': {3, 4, 9, 11, 12, 15, 16, 18},
                  'show_perms': {2, 3, 4, 9, 11, 12, 15, 16, 18, 22, 23},
                  'read_perms': {2, 3, 4, 9, 11, 12, 15, 16, 18, 22, 23},
                  'reply_perms': {3, 4, 9, 11, 12, 15, 16, 18}}

    def test_0010_parse_byte(self):
        ref = (b'a:5:{s:11:"start_perms";s:20:"3,9,12,15,16,18,4,11";'
               b's:11:"reply_perms";s:20:"3,9,12,15,16,18,4,11"'
               b';s:10:"read_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";'
               b's:12:"upload_perms";s:20:"3,9,12,15,16,18,4,11";'
               b's:10:"show_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";}')
        perms = parse_permissions(ref)
        print(perms)
        self.assertEqual(perms, self.parsed_ref)

    def test_0020_parse_unicode(self):
        ref = ('a:5:{s:11:"start_perms";s:20:"3,9,12,15,16,18,4,11";'
               's:11:"reply_perms";s:20:"3,9,12,15,16,18,4,11";'
               's:10:"read_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";'
               's:12:"upload_perms";s:20:"3,9,12,15,16,18,4,11";'
               's:10:"show_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";}')
        perms = parse_permissions(ref)
        print(perms)
        self.assertEqual(perms, self.parsed_ref)

    def test_0030_no_permissions(self):
        perms = parse_permissions("")
        self.assertEqual(perms, {})


class TestForumPermissions(unittest.TestCase):
    permission_types = (ForumPermissions.PERM_READ,
                        ForumPermissions.PERM_REPLY,
                        ForumPermissions.PERM_START,
                        ForumPermissions.PERM_UPLOAD,
                        ForumPermissions.PERM_SHOW)
    permission_full_ref = ('a:5:{'
                           's:11:"start_perms";s:20:"1,2,3,4,5,6,7,8,9,10";'
                           's:11:"reply_perms";s:20:"1,2,3,4,5,6,7,8,9,10";'
                           's:10:"read_perms";s:20:"1,2,3,4,5,6,7,8,9,10";'
                           's:12:"upload_perms";s:20:"1,2,3,4,5,6,7,8,9,10";'
                           's:10:"show_perms";s:20:"1,2,3,4,5,6,7,8,9,10";}')
    permission_empty_ref = ('a:5:{'
                            's:11:"start_perms";s:0:"";'
                            's:11:"reply_perms";s:0:"";'
                            's:10:"read_perms";s:0:"";'
                            's:12:"upload_perms";s:0:"";'
                            's:10:"show_perms";s:0:"";}')

    def test_0010_full_positive_single(self):
        perm = ForumPermissions(self.permission_full_ref)
        for permission in self.permission_types:
            for mask in range(1, 11):
                self.assertTrue(perm.is_fulfilled((mask,), permission))

    def test_0020_full_negative_single(self):
        perm = ForumPermissions(self.permission_full_ref)
        for permission in self.permission_types:
            for mask in (0, 11):
                self.assertFalse(perm.is_fulfilled((mask,), permission))

    def test_0030_empty_permissions_single(self):
        perm = ForumPermissions(self.permission_empty_ref)
        for permission in self.permission_types:
            for mask in range(0, 11):
                self.assertFalse(perm.is_fulfilled((mask,), permission))

    def test_0040_test_positive_multi(self):
        perm = ForumPermissions(self.permission_full_ref)
        for permission in self.permission_types:
            self.assertTrue(perm.is_fulfilled((1, 2, 12), permission))

    def test_0050_no_permissions(self):
        perm = ForumPermissions("")
        for permission in self.permission_types:
            for mask in range(0, 11):
                self.assertFalse(perm.is_fulfilled((mask,), permission))


class TestUserBanning(unittest.TestCase):
    def _make_ban(self, start, end=None, duration=9999, unit="d"):
        if not end:
            end = timestamps.new_datetime(year=MAXYEAR, day=31, month=12)

        return "%d:%d:%d:%s" % (start.timestamp(),
                                end.timestamp(),
                                duration,
                                unit)

    def test_0010_ban_active(self):
        ban = UserBan.from_banline(self._make_ban(timestamps.now_datetime() - timedelta(days=1)))
        self.assertTrue(ban.is_active())

    def test_0020_ban_expired(self):
        now = timestamps.now_datetime()
        ban = UserBan.from_banline(self._make_ban(now - timedelta(days=3), now - timedelta(days=1), unit="h"))
        self.assertFalse(ban.is_active())

    def test_0020_ban_not_started(self):
        now = timestamps.now_datetime()
        ban = UserBan.from_banline(self._make_ban(now + timedelta(days=3), now + timedelta(days=1), unit="h"))
        self.assertFalse(ban.is_active())
