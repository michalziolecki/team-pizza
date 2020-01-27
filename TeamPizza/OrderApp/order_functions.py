from .models import Order, ContributionOrder
from UserApp.models import PizzaUser
from django.conf import settings
import logging
from logging import Logger
from django.db import Error as DB_Error


def user_already_joined(hash_id: str, user: PizzaUser) -> bool:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    contrib_exist = False
    try:
        order = Order.objects.filter(hash_id=hash_id).get()
        contrib_exist = ContributionOrder.objects.filter(order=order, contribution_owner=user).exists()
    except DB_Error as db_err:
        logger.error(f'Checking contribution for {user.username} failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Checking contribution for {user.username} failed ! Base exception cached info: {be.args}')

    return contrib_exist
