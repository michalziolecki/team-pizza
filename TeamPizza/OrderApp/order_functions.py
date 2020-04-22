from .models import Order, ContributionOrder
from UserApp.models import PizzaUser
from django.conf import settings
import logging
from logging import Logger
from django.db import Error as DB_Error
from django.utils import timezone
from django.conf import settings


def user_max_joined(hash_id: str, user: PizzaUser) -> bool:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    contrib_exist = False
    contributes = 0
    try:
        order = Order.objects.filter(hash_id=hash_id).get()
        contributes = ContributionOrder.objects.filter(order=order, contribution_owner=user).count()

    except DB_Error as db_err:
        logger.error(f'Checking contribution for {user.username} failed ! info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Checking contribution for {user.username} failed ! Base exception cached info: {be.args}')

    return contributes > settings.MAX_CONTRIBUTES


def close_after_deadline(hash_id: str) -> Order:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    contrib_exist = False
    try:
        order = Order.objects.filter(hash_id=hash_id).get()
        actual_time = timezone.now()
        print(f'TEST order.prediction_order_time: {order.prediction_order_time}')
        print(f'TEST actual_time: {actual_time}')
        if order.prediction_order_time < actual_time:
            print(f'TEST {order.prediction_order_time > actual_time}')
            Order.objects.filter(hash_id=hash_id).update(
                is_open=False,
                close_time=order.prediction_order_time
            )
        return order
    except DB_Error as db_err:
        logger.error(f'Updating order after deadline failed ! Order id: {hash_id}, info: {db_err.args}')
    except BaseException as be:
        logger.error(f'Updating order after deadline failed ! Order id: {hash_id}, info: {be.args}')

    return None
