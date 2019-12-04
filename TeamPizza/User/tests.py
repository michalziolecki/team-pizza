from django.test import TestCase
from .user_functions import hash_and_salt_password
from unittest import TestCase as BaseTestCase


class TestCheck_user_role(TestCase):
    def test_check_user_role(self):
        self.fail()


class TestHash_and_salt_password(BaseTestCase):
    def test_hash_and_salt_password(self):
        # input
        password = 'AlaMaKota'

        # expected
        expected_hash_with_salt = ''

        # test
        result = hash_and_salt_password(password=password, salt_size=30)
        self.assertEqual(expected_hash_with_salt, result)

    # def test_verify_password(self):
    #     # input
    #     hash_with_salt = ''
    #
    #     # expected
    #     expected_decrypted = 'AlaMaKota'
    #
    #     # test
    #     result = hash_and_salt_password(password=password, salt_size=30)
    #
    #     self.assertEqual(, result)