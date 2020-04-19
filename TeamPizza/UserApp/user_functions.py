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
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from .models import RestorePassword
import re

from .models import PizzaUser, LoginInformation, ConfirmAccount


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


def is_superuser_by_role(role: str) -> bool:
    is_super_user = False
    if role != 'U':
        is_super_user = True
    return is_super_user


def is_root_by_role(role: str) -> bool:
    is_root = False
    if role == 'R':
        is_root = True
    return is_root


def check_user_role(login: str) -> str:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    role = ''

    try:
        user = PizzaUser.objects.get(username=login)
        role: str = user.role
    except ObjectDoesNotExist as ne:
        logger.info(f'User not found by login {ne.args}')

    if not role:
        try:
            user = PizzaUser.objects.get(email=login)
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
    password = ''.join([final_pwd_hash, base64_salt])
    return password


def verify_password(password: str, stored_password: str) -> bool:
    salt_len = 172
    base64_salt: str = stored_password[-salt_len:]
    pwd = ''.join([password, base64_salt])
    pwd_hash = hashlib.sha3_512(pwd.encode('ascii')).hexdigest()
    hex_pwd = ''.join([pwd_hash, base64_salt])
    base64_pwd: bytes = base64.b64encode(hex_pwd.encode('ascii'))
    final_pwd_hash: str = str(base64_pwd, 'ascii')
    return ''.join([final_pwd_hash, base64_salt]) == stored_password


def insert_new_user_into_db(request: WSGIRequest, logger: Logger) -> tuple:
    user = request.user
    post_body: QueryDict = request.POST
    params: dict = post_body.dict()
    template = 'UserApp/sign-up-success.html'
    pwd_regex = re.compile('.{9,}')
    confirm_token = ''
    try:
        if params['password'] != params['confirm_password'] or not pwd_regex.match(params['password']):
            template = 'UserApp/password-not-confirmed.html'
        else:
            password_hash = hash_and_salt_password(params['password'])
            new_user = PizzaUser(
                is_active=False,
                username=params['nickname'],
                first_name=params['name'],
                last_name=params['surname'],
                email=params['mail'],
                password=password_hash,
                role=params['role'],
                is_superuser=is_superuser_by_role(params['role'])
            )
            new_user.save()
            logger.debug(f'New user is {new_user.username}')
            confirm_token = default_token_generator.make_token(new_user)
            token_expires = timezone.now() + timezone.timedelta(hours=24)
            logger.debug(f'Generated token for user {new_user.username} is "{confirm_token}"'
                         f' and expire at "{token_expires}"')
            confirm_entity = ConfirmAccount(
                user=new_user,
                token=confirm_token,
                deadline=token_expires
            )
            confirm_entity.save()
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

    return template, confirm_token


def update_user_info_while_login(request: WSGIRequest, user: PizzaUser):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    try:
        PizzaUser.objects.filter(username=user.username).update(is_logged=True,
                                                                last_login=timezone.now())
        logger.info('Update user object success while login!')
        last_log_ip = get_client_ip(request, user)
        if last_log_ip:
            db_user = PizzaUser.objects.filter(username=user.username).get()
            last_log_info = LoginInformation(user=db_user, last_login=timezone.now(), ip_login=last_log_ip)
            last_log_info.save()
            logger.info('Added user login information history success!')
        else:
            logger.warning('IP address of user not found!')
    except DB_Error as db_err:
        logger.error(f'Update user fields while login or login information entity failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Update user entities while login failed ! Base exception cached info: {be.args}')


def get_client_ip(request: WSGIRequest, user: PizzaUser):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    real_ip = request.META.get('HTTP_X_REAL_IP')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    logger.info(f'User {user.username}, log to service with forwarded addresses: {x_forwarded_for}')
    if real_ip:
        ip = real_ip
    elif x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def update_user_info_while_logout(user: PizzaUser):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    try:
        PizzaUser.objects.filter(username=user.username).update(is_logged=False)
        logger.info('Update user object success while logout!')
    except DB_Error as db_err:
        logger.error(f'Update user fields while logout failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Update user while logout failed ! Base exception cached info: {be.args}')


def get_last_user_login(user: PizzaUser) -> list:
    db_user = get_user_from_db(user.username)
    login_list = []
    if db_user:
        login_list = LoginInformation.objects.filter(user=db_user).order_by('-last_login')[:10]
    return login_list


def get_user_from_db(username: str) -> PizzaUser:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    db_user = None
    try:
        db_user = PizzaUser.objects.filter(username=username).get()
    except DB_Error as db_err:
        logger.error(f'Getting user from database failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Getting user from database failed ! Base exception cached info: {be.args}')
    return db_user


def get_user_from_db_by_mail(mail: str) -> PizzaUser:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    db_user = None
    try:
        db_user = PizzaUser.objects.filter(email=mail).get()
    except DB_Error as db_err:
        logger.error(f'Getting user from database failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Getting user from database failed ! Base exception cached info: {be.args}')
    return db_user


def create_token_to_restore_pwd(restored_user: PizzaUser) -> tuple:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    confirm_token = ''
    status = True
    if restored_user:
        logger.debug('user exist')
        confirm_token = default_token_generator.make_token(restored_user)
        logger.debug('token created')
        try:
            token_expires = timezone.now() + timezone.timedelta(hours=3)
            logger.debug(f'token expires at {token_expires}')
            if RestorePassword.objects.filter(user=restored_user,
                                              token=confirm_token).exists():
                logger.debug(f'token exist')
                RestorePassword.objects.filter(user=restored_user,
                                               token=confirm_token).delete()
                logger.debug(f'token deleted')
            restore_entity = RestorePassword(
                user=restored_user,
                token=confirm_token,
                deadline=token_expires
            )
            restore_entity.save()
            logger.debug(f'token saved')
        except BaseException as be:
            logger.debug(f'exception cached: {be.args}')
            status = False
    return status, confirm_token
