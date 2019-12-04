from .models import User
import logging
from logging import Logger
from django.db import Error as DB_Error
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import hashlib, os, base64


def is_usual_user_and_exist(login: str) -> tuple:
    is_usual = True
    exist = True

    if login:
        try:
            role: str = check_user_role(login)
            if role != 'U':
                is_usual = False
        except ObjectDoesNotExist as ne:
            is_usual = False
            exist = False
    else:
        is_usual = False
        exist = False

    return is_usual, exist


def check_user_role(login: str) -> str:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    role = ''

    try:
        user = User.objects.get(surname=login)
        role: str = user.role
    except ObjectDoesNotExist as ne:
        logger.info(f'User not found by login {ne.args}')

    if not role:
        try:
            user = User.objects.get(mail=login)
            role = user.role
        except ObjectDoesNotExist as ne:
            logger.error(f'User not found by mail {ne.args}')
            raise ObjectDoesNotExist(f'{login} doesnt exist !')

    return role


def hash_and_salt_password(password: str, salt_size=settings.SALT) -> str:
    # creating salt
    salt: str = hashlib.sha3_512(os.urandom(salt_size)).hexdigest()
    encoded_salt: bytes = base64.b64encode(salt.encode('ascii'))
    base64_salt: str = str(encoded_salt, 'ascii')

    # hashing password
    pwd = ''.join([password, base64_salt])
    hex_pwd = ''.join([hashlib.sha3_512(pwd).hexdigest(), base64_salt])
    base64_pwd: bytes = base64.b64encode(hex_pwd.encode('ascii'))
    pwd_hash: str = str(base64_pwd, 'ascii')
    return pwd_hash


def verify_password(password: str, stored_password: str, salt_size=settings.SALT) -> str:
    base64_salt: str = stored_password[-salt_size:]
    encoded_salt: bytes = base64.b64decode(base64_salt)
    salt: str = encoded_salt.decode('ascii')
    return salt