import base64
import hashlib
import logging
import os
from logging import Logger

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.db import Error as DB_Error
from django.http.request import QueryDict

from .models import User


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


def hash_and_salt_password(password: str) -> str:
    # creating salt
    random_size = 30
    salt: str = hashlib.sha3_512(os.urandom(random_size)).hexdigest()
    encoded_salt: bytes = base64.b64encode(salt.encode('ascii'))
    base64_salt: str = str(encoded_salt, 'ascii')

    # hashing password
    pwd = ''.join([password, base64_salt])
    pwd_hash = hashlib.sha3_512(pwd.encode('ascii')).hexdigest()
    hex_pwd = ''.join([pwd_hash, base64_salt])
    base64_pwd: bytes = base64.b64encode(hex_pwd.encode('ascii'))
    final_pwd_hash: str = str(base64_pwd, 'ascii')
    return ''.join([final_pwd_hash, base64_salt])


def verify_password(password: str, stored_password: str) -> bool:
    salt_len = 172
    base64_salt: str = stored_password[-salt_len:]
    pwd = ''.join([password, base64_salt])
    pwd_hash = hashlib.sha3_512(pwd.encode('ascii')).hexdigest()
    hex_pwd = ''.join([pwd_hash, base64_salt])
    base64_pwd: bytes = base64.b64encode(hex_pwd.encode('ascii'))
    final_pwd_hash: str = str(base64_pwd, 'ascii')
    return ''.join([final_pwd_hash, base64_salt]) == stored_password


def insert_new_user_into_db(request: WSGIRequest, logger: Logger) -> str:
    user = request.user
    post_body: QueryDict = request.POST
    params: dict = post_body.dict()
    template = 'sign-up-success.html'

    try:
        if params['password'] != params['confirm_password']:
            template = 'TeamPizza/password-not-confirmed.html'
        else:
            password_hash = hash_and_salt_password(params['password'])
            new_user = User(
                name=params['name'],
                surname=params['surname'],
                nick_name=params['nickname'],
                mail=params['mail'],
                password_hash=password_hash,
                role=params['role']
            )
            new_user.save()
    except KeyError as ke:
        logger.error(f'Sign up method failed while parsing params! info -> params: {params},'
                     f' user: {user.username}, dict exception info: {ke.args}')
        template = 'TeamPizza/method-error.html'
    except DB_Error as db_err:
        logger.error(f'Sign up method failed while entity save into db! info -> body: {request.body},'
                     f' user: {user.username}, django.db exception info: {db_err.args}')
        template = 'TeamPizza/method-error.html'
    except BaseException as be:
        logger.error(f'Sign up method failed ! info -> body: {request.body},'
                     f' user: {user.username}, base exception info: {be.args}')
        template = 'TeamPizza/method-error.html'

    return template
