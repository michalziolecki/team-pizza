from .models import User
import logging
from logging import Logger
from django.db import Error as DB_Error
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


def check_user_role(login: str) -> str:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    role = ''
    try:
        user = User.objects.get(surname=login)
        role = user.role
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
    pass
