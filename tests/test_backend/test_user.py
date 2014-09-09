import unittest
from db_backend.utils.user import exma_passhash, ApiUser, GUEST_MASK, parse_permissions


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
               's:11:"reply_perms";s:20:"3,9,12,15,16,18,4,11"'
               ';s:10:"read_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";'
               's:12:"upload_perms";s:20:"3,9,12,15,16,18,4,11";'
               's:10:"show_perms";s:28:"2,3,9,12,15,16,18,22,23,4,11";}')
        perms = parse_permissions(ref)
        print(perms)
        self.assertEqual(perms, self.parsed_ref)
