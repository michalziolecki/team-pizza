from unittest import TestCase
import unittest.mock as mock
from unittest.mock import MagicMock
from User.models import PizzaUser
from User.user_functions import check_user_role, is_usual_user_and_exist


class TestCheckUserRole(TestCase):

    @mock.patch('UserApp.models.UserApp.objects')
    def test_check_user_role(self, user_mock: MagicMock):
        # input
        login = 'name'
        user_mock.get.return_value = PizzaUser(
            # id=1,
            name='name',
            surname='surname',
            nick_name='nickname',
            mail='mail',
            password_hash='password_hash',
            role='A'
        )

        # expected
        role = 'A'

        # test
        result = check_user_role(login)
        self.assertEqual(role, result)

    @mock.patch('UserApp.user_functions.check_user_role')
    def test_is_usual_user_and_exist(self, user_role_mock):
        # input
        user_role_mock.return_value = 'U'
        user_role, exist = is_usual_user_and_exist('test')

        # test
        self.assertTrue(user_role)
        self.assertTrue(exist)
