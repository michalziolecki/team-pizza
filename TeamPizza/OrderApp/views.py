from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from django.db import Error as DB_Error

import logging
from logging import Logger
from datetime import datetime

from UserApp.models import PizzaUser
from UserApp.user_functions import get_user_from_db


@login_required(login_url='/login-required')
def order_options_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'OrderApp/order-options-view.html', context)


@login_required(login_url='/login-required')
def opened_order_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'OrderApp/opened-order-view.html', context)


@login_required(login_url='/login-required')
def create_order(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == 'POST' and user.is_authenticated:
        predicted_datetime = ''
        description = ''

        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            predicted_datetime = params['predict-order-time']
            description = params['description']
        except KeyError as ke:
            logger.error(f'Key error while user try create order, probably someone change form!'
                         f'  info: {ke.args}')

        db_user: PizzaUser = get_user_from_db(user.username)
        parsed_datetime = datetime.strptime(predicted_datetime, "%Y-%m-%dT%H:%M")

        if datetime.now() < parsed_datetime and db_user:
            try:
                # insert order into db
                # return redirect('/order/options/')
                pass
            except DB_Error as db_err:
                logger.error(f'Create order by user {user.username} failed ! info: {db_err.args}')
                context['bad_param'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Create order by user {user.username} failed ! Base exception cached info: {be.args}')
                context['bad_param'] = 'Problem with database try again'
        else:
            context['bad_param'] = 'Date is incorrect'

        return render(request, 'OrderApp/order-options-view.html', context)

    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context)
    else:
        return render(request, 'TeamPizza/bad-method.html', context)


@login_required(login_url='/login-required')
def close_order(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    # POST method to close order in db
    return render(request, 'OrderApp/order-closed.html', context)


@login_required(login_url='/login-required')
def delete_order(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    # POST method to delete order in db
    return render(request, 'OrderApp/order-deleted.html', context)


@login_required(login_url='/login-required')
def join_order_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    # view of form to join
    return render(request, 'OrderApp/join-order-view.html', context)


@login_required(login_url='/login-required')
def join_order(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    # POST method to add preferences to order in db
    return render(request, 'OrderApp/order-options-view.html', context)
