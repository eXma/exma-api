import unittest
from db_backend.utils.user import exma_passhash, ApiUser, GUEST_MASK


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