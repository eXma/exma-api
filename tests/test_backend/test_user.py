import unittest
from db_backend.utils.user import exma_passhash


class TestPasswordHandling(unittest.TestCase):
    def test_0010_valid_password(self):
        hash = exma_passhash("test", "abc")
        self.assertEqual(hash, '57378fa5f7f15da155244b48622b2749')

    def test_0020_invalid_password(self):
        hash = exma_passhash("peng", "abc")
        self.assertNotEqual(hash, '57378fa5f7f15da155244b48622b2749')

    def test_0020_invalid_salt(self):
        hash = exma_passhash("test", "peng")
        self.assertNotEqual(hash, '57378fa5f7f15da155244b48622b2749')
