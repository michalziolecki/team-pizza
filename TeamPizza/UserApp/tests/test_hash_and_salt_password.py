from User.user_functions import verify_password, hash_and_salt_password
from unittest import TestCase as BaseTestCase


class TestHashAndSaltPassword(BaseTestCase):
    maxDiff = None

    def test_hash_and_salt_password(self):
        # input
        password = 'AlaMaKota'

        # test
        first_result = hash_and_salt_password(password=password)
        second_result = hash_and_salt_password(password=password)
        self.assertNotEqual(first_result, second_result)

    def test_verify_password(self):
        # input
        password = 'AlaMaKota'
        wrong_password = 'AlaKotaNieMa'
        existing_password = 'ZGQyZDk4NTRmZGQyMGYwMTQyMjIxN2RjYjlhOGEyYTBjZGEzMmU3OWU4ZGNlMzU2ZmI3YzgyYThmNzE2ODczZWYxOWIwYzA4YjNmOGZmY2I3OTg3ZDgzNzc4OTEyMjZjZjkzZWExYmJmZTk5YjZhZTcwMjA1MjA1ZTUzNzhjMTBZVFUzTlRGa1ltVTNabU01TXpoaU1EWXlNMkptTm1NNE5UZ3lNakEzTmpJd09UQTJaR1U0TVdJMFlUa3hORE5sTXpRek16azVORE5tTkRGak5qRm1aV1E1WXpVMU1HWTFaRE0zTURVd09XRXpZemN5T1dVellXWmxPVFJpT1dJMU9UWmhabVV6TXpJeE1tUmtZbVkzWVROaFlUZzJaVFV3WkRNek1XTXpaVEE9YTU3NTFkYmU3ZmM5MzhiMDYyM2JmNmM4NTgyMjA3NjIwOTA2ZGU4MWI0YTkxNDNlMzQzMzk5NDNmNDFjNjFmZWQ5YzU1MGY1ZDM3MDUwOWEzYzcyOWUzYWZlOTRiOWI1OTZhZmUzMzIxMmRkYmY3YTNhYTg2ZTUwZDMzMWMzZTA='

        # test
        result = verify_password(password=password, stored_password=existing_password)
        result_failed = verify_password(password=wrong_password, stored_password=existing_password)

        self.assertTrue(result)
        self.assertFalse(result_failed)
