from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from django.db import Error as DB_Error

import os
import hashlib
import logging
from logging import Logger
from datetime import datetime
from hashids import Hashids

from UserApp.models import PizzaUser
from UserApp.user_functions import get_user_from_db
from .models import Order, ContributionOrder
from OrderApp import HASH_IDS_LENGTH


@login_required(login_url='/login-required')
def order_options_view(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == 'GET' and user.is_authenticated:
        db_user = get_user_from_db(user.username)
        if db_user:
            try:
                context['order_list'] = Order.objects.filter(is_open=True).order_by('prediction_order_time')
            except DB_Error as db_err:
                logger.error(f'Getting orders from database failed ! info: {db_err.args}')
                context['bad_param'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Getting orders from database failed !'
                             f' Base exception cached info: {be.args}')
                context['bad_param'] = 'Problem with database try again'

        return render(request, 'OrderApp/order-options-view.html', context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def opened_order_view(request: WSGIRequest, hash_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == 'GET' and user.is_authenticated:
        logger.debug('Get method opened_order_view')
        db_user = get_user_from_db(user.username)
        if db_user:
            try:
                order = Order.objects.filter(hash_id=hash_id).get()
                contributions = ContributionOrder.objects.filter(order=order).order_by('add_contr_time')
                # pobrać powiązane encje
                small_pieces = 0
                big_pieces = 0
                logger.debug(f'contributions size: {len(contributions)}')
                for piece in [contribute for contribute in contributions if contribute.size == 'B']:
                    big_pieces += piece.pieces_number
                for piece in [contribute for contribute in contributions if contribute.size == 'S']:
                    small_pieces += piece.pieces_number
                context['contributions'] = contributions
                context['order'] = order
                context['small_pieces'] = small_pieces
                context['big_pieces'] = big_pieces
                context['all_pieces'] = small_pieces + big_pieces
            except DB_Error as db_err:
                logger.error(f'Getting order "{hash_id}" from database failed ! info: {db_err.args}')
                context['bad_param'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Getting order "{hash_id}" from database failed !'
                             f' Base exception cached info: {be.args}')
                context['bad_param'] = 'Problem with database try again'

        return render(request, 'OrderApp/opened-order-view.html', context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


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
        actual_time = datetime.now()

        if actual_time < parsed_datetime and db_user:
            try:
                hash_id: str = hashlib.sha1(os.urandom(HASH_IDS_LENGTH)).hexdigest()
                logger.debug(f'Hash_id created!  "{hash_id}" in type {type(hash_id)}, length {len(hash_id)}')
                order = Order(order_owner=db_user,
                              hash_id=hash_id,
                              prediction_order_time=predicted_datetime,
                              description=description,
                              is_open=True,
                              open_time=actual_time)
                order.save()
                logger.debug(f'Order added! by user: {db_user.username}')
                return redirect('/order/options/')
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
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


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
def join_order_view(request: WSGIRequest, hash_id: str):
    user = request.user
    context = {'user': user,
               'hash_id': hash_id
               }
    return render(request, 'OrderApp/join-order-view.html', context)


@login_required(login_url='/login-required')
def join_order(request: WSGIRequest, hash_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == 'POST' and user.is_authenticated:
        pieces = ''
        size = ''
        description = ''

        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            pieces = params['pieces']
            size = params['size']
            description = params['description']
        except KeyError as ke:
            logger.error(f'Key error while user try join to order, probably someone change form!'
                         f'  info: {ke.args}')

        db_user: PizzaUser = get_user_from_db(user.username)

        pieces_int = 0
        if pieces:
            try:
                pieces_int = int(pieces)
            except ValueError as ve:
                logger.error(f'Value error while user try join to order, number of pieces was not integer!'
                             f'  info: {ve.args}')

        if pieces_int > 0 and size and db_user:
            try:
                order = Order.objects.filter(hash_id=hash_id).get()
                contribution = ContributionOrder(
                    contribution_owner=db_user,
                    order=order,
                    pieces_number=int(pieces),
                    size=size,
                    add_contr_time=datetime.now(),
                    was_updated=False,
                    description=description
                )
                contribution.save()
                logger.debug(f'User: {db_user.username} join to order "{hash_id}"! ')
                return redirect(f'/order/preview-order/{hash_id}/')
            except DB_Error as db_err:
                logger.error(f'Create order by user {user.username} failed ! info: {db_err.args}')
                context['bad_param'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Create order by user {user.username} failed ! Base exception cached info: {be.args}')
                context['bad_param'] = 'Problem with database try again'
        else:
            context['bad_param'] = 'Data is incorrect'
        return render(request, 'OrderApp/join-order-view.html', context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)
