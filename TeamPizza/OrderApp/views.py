from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from django.db import DatabaseError as DB_Error

import os
import hashlib
import logging
from logging import Logger
from datetime import datetime
from django.utils import timezone
from hashids import Hashids

from UserApp.models import PizzaUser
from UserApp.user_functions import get_user_from_db
from .models import Order, ContributionOrder
from OrderApp import HASH_IDS_LENGTH
from .order_functions import user_already_joined, close_after_deadline


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
                context['close_order_list'] = Order.objects.filter(is_open=False).order_by('close_time')[:5]
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
                actual_time = timezone.now()
                if order.prediction_order_time < actual_time:
                    closed_order = close_after_deadline(hash_id=hash_id)
                    if closed_order:
                        order = closed_order
                contributions = ContributionOrder.objects.filter(order=order).order_by('add_contr_time')
                small_pieces = 0
                big_pieces = 0
                other_meal = 0
                logger.debug(f'contributions size: {len(contributions)}')
                for piece in [contribute for contribute in contributions if contribute.ord_type == 'B']:
                    big_pieces += piece.number
                for piece in [contribute for contribute in contributions if contribute.ord_type == 'S']:
                    small_pieces += piece.number
                for other in [contribute for contribute in contributions if contribute.ord_type == 'O']:
                    other_meal += other.number
                context['contributions'] = contributions
                context['order'] = order
                context['small_pieces'] = small_pieces
                context['big_pieces'] = big_pieces
                context['all_pieces'] = small_pieces + big_pieces
                context['other_meal'] = other_meal
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
    if request.method == 'POST' and user.is_authenticated and user.role != 'U':
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
        parsed_datetime = timezone.make_aware(datetime.strptime(predicted_datetime, "%Y-%m-%dT%H:%M"))
        actual_time = timezone.now()

        if description == 'Your order description...':
            description = ''

        if actual_time < parsed_datetime and db_user:
            try:
                hash_id: str = hashlib.sha1(os.urandom(HASH_IDS_LENGTH)).hexdigest()
                logger.debug(f'Hash_id created!  "{hash_id}" in type {type(hash_id)}, length {len(hash_id)}')
                order = Order(order_owner=db_user,
                              hash_id=hash_id,
                              prediction_order_time=parsed_datetime,
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

    elif not user.is_authenticated or user.role == 'U':
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def update_order(request: WSGIRequest, hash_id: str):
    user = request.user
    close_after_deadline(hash_id=hash_id)
    if request.method == "POST" and user.is_authenticated:
        return update_order_post(request, hash_id)
    elif request.method == "GET" and user.is_authenticated:
        return update_order_get(request, hash_id)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', status=400)


def update_order_get(request: WSGIRequest, hash_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if hash_id:
        try:
            order = Order.objects.filter(hash_id=hash_id).get()
            if order.order_owner.id == user.id and order.is_open:
                context['order'] = order
                context['hash_id'] = hash_id
                return render(request, 'OrderApp/order-update.html', context)
            elif not order.is_open:
                context['bad_param'] = f'Order has been closed at {order.close_time}'
                return render(request, 'TeamPizza/not-authenticated.html', context)
            else:
                return render(request, 'TeamPizza/not-authenticated.html', status=401)
        except DB_Error as db_err:
            logger.error(f'Generating update order view by user {user.username} failed ! info: {db_err.args}')
            context['bad_param'] = 'Not found in data base'
        except BaseException as be:
            logger.error(
                f'Generating update order view by user {user.username} failed ! Base exception cached info: {be.args}')
            context['bad_param'] = 'Not found in data base'

        return render(request, 'OrderApp/order-not-exist.html', context, status=404)
    return render(request, 'TeamPizza/operation-failed.html', context, status=400)


def update_order_post(request: WSGIRequest, hash_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user', user}
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

    # if description == 'Your order description...':
    #     description = ''
    db_user: PizzaUser = get_user_from_db(user.username)
    parsed_datetime = timezone.make_aware(datetime.strptime(predicted_datetime, "%Y-%m-%dT%H:%M"))
    actual_time = timezone.now()

    if actual_time < parsed_datetime and db_user:
        try:
            order = Order.objects.filter(hash_id=hash_id).get()
            if order and order.is_open and order.order_owner.id == user.id:
                Order.objects.filter(hash_id=hash_id).update(
                    prediction_order_time=parsed_datetime,
                    description=description,
                    open_time=actual_time)
                logger.debug(f'Order updated! by user: {db_user.username}')
                return redirect('/order/options/')
            elif not order.is_open:
                context['bad_param'] = f'Order has been closed at {order.close_time}'
                return render(request, 'TeamPizza/not-authenticated.html', context)
            else:
                return render(request, 'TeamPizza/not-authenticated.html', status=401)
        except DB_Error as db_err:
            logger.error(f'Update order by user {user.username} failed ! info: {db_err.args}')
            context['bad_param'] = 'Problem with database try again'
        except BaseException as be:
            logger.error(f'Update order by user {user.username} failed ! Base exception cached info: {be.args}')
            context['bad_param'] = 'Problem with database try again'
        return render(request, 'OrderApp/order-not-exist.html', context, status=404)
    else:
        context['bad_param'] = 'Date is incorrect'

    return render(request, 'OrderApp/order-update.html', context)


@login_required(login_url='/login-required')
def close_order(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == "POST" and user.is_authenticated:
        hash_id = get_one_item_from_post(request)
        if hash_id:
            try:
                order = Order.objects.filter(hash_id=hash_id).get()
                if order and order.order_owner.id == user.id:
                    Order.objects.filter(hash_id=hash_id).update(
                        is_open=False,
                        close_time=timezone.now()
                    )
                    return redirect(f'/order/preview-order/{hash_id}')
            except DB_Error as db_err:
                logger.error(f'Close order by user {user.username} failed ! info: {db_err.args}')
                context['bad_param'] = 'Something went wrong, try again'
            except BaseException as be:
                logger.error(f'Close order by user {user.username} failed ! Base exception cached info: {be.args}')
                context['bad_param'] = 'Something went wrong, try again'
            return redirect('/operation-failed/')

    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


def get_one_item_from_post(request: WSGIRequest, item_name='hash_id') -> str:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    item = ''
    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        item = params[item_name]
    except KeyError as ke:
        logger.error(f'Key error while user try remove order, probably someone change form!'
                     f'  info: {ke.args}')
    return item


@login_required(login_url='/login-required')
def delete_order(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == "POST" and user.is_authenticated:
        hash_id = get_one_item_from_post(request)
        try:
            order = Order.objects.filter(hash_id=hash_id).get()
            if order and order.order_owner.id == user.id:
                Order.objects.filter(hash_id=hash_id).delete()
                return redirect('/operation-success/')
        except DB_Error as db_err:
            logger.error(f'Delete order by user {user.username} failed ! info: {db_err.args}')
            context['bad_param'] = 'Something went wrong, try again'
        except BaseException as be:
            logger.error(f'Delete order by user {user.username} failed ! Base exception cached info: {be.args}')
            context['bad_param'] = 'Something went wrong, try again'
        return redirect('/operation-failed/')
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def delete_contribution(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}

    if request.method == "POST" and user.is_authenticated:

        hash_id = ''
        contribution_id = ''
        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            hash_id = params['hash_id']
            contribution_id = params['contribution_id']
        except KeyError as ke:
            logger.error(f'Key error while user try remove order contribution, probably someone change form!'
                         f'  info: {ke.args}')

        if hash_id and contribution_id:
            try:
                order = Order.objects.filter(hash_id=hash_id).get()
                actual_time = timezone.now()
                if order.prediction_order_time < actual_time:
                    order = close_after_deadline(hash_id=hash_id)
                contribution = ContributionOrder.objects \
                    .filter(id=contribution_id, order=order).get()
                logger.debug(f'User id is: {user.id} !')
                if contribution and contribution.contribution_owner.id == user.id \
                        and order is not None and order.is_open:
                    ContributionOrder.objects.filter(id=contribution_id, order=order).delete()
                    logger.info(f'Delete order contribution by user {user.username} success !')
                    return redirect('/operation-success/')
                elif order is None or not order.is_open:
                    context['bad_param'] = f'Order has been closed at {order.close_time}'
                    return render(request, 'TeamPizza/not-authenticated.html', context)
            except DB_Error as db_err:
                logger.error(f'Delete order by user {user.username} failed ! info: {db_err.args}')
                context['bad_param'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Delete order by user {user.username} failed ! Base exception cached info: {be.args}')
                context['bad_param'] = 'Problem with database try again'
        else:
            context['bad_param'] = 'Bad params! Someone change form!'
        return redirect('/operation-failed/')
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def update_contribution(request: WSGIRequest, hash_id: str, contribution_id: str):
    user = request.user
    close_after_deadline(hash_id=hash_id)
    if request.method == "POST" and user.is_authenticated:
        return update_contribution_post(request, hash_id, contribution_id)
    elif request.method == "GET" and user.is_authenticated:
        return update_contribution_get(request, hash_id, contribution_id)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', status=400)


@login_required(login_url='/login-required')
def update_contribution_get(request: WSGIRequest, hash_id: str, contribution_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if hash_id and contribution_id:
        try:
            order = Order.objects.filter(hash_id=hash_id).get()
            contribution = ContributionOrder.objects.filter(id=contribution_id, order=order).get()
            if contribution.contribution_owner.id == user.id and order.is_open:
                context['contribution'] = contribution
                context['hash_id'] = hash_id
                context['contribution_id'] = contribution_id
                return render(request, 'OrderApp/contribution-update.html', context)
            elif not order.is_open:
                context['bad_param'] = f'Order has been closed at {order.close_time}'
                return render(request, 'TeamPizza/not-authenticated.html', context)
            else:
                return render(request, 'TeamPizza/not-authenticated.html', status=401)
        except DB_Error as db_err:
            logger.error(f'Generating update contribution view by user {user.username} failed ! info: {db_err.args}')
            context['bad_param'] = 'Not found in data base'
        except BaseException as be:
            logger.error(
                f'Generating update contribution view by user {user.username} failed ! Base exception cached info: {be.args}')
            context['bad_param'] = 'Not found in data base'

        return render(request, 'OrderApp/contribution-not-exist.html', context, status=404)
    return render(request, 'TeamPizza/operation-failed.html', context, status=400)


@login_required(login_url='/login-required')
def update_contribution_post(request: WSGIRequest, hash_id: str, contribution_id: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    pieces = ''
    ord_type = ''
    description = ''

    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        pieces = params['pieces']
        ord_type = params['ord_type']
        description = params['description']
    except KeyError as ke:
        logger.error(f'Key error while user try update contribution order, probably someone change form!'
                     f'  info: {ke.args}')

    if hash_id and contribution_id:
        try:
            order = Order.objects.filter(hash_id=hash_id).get()
            contribution = ContributionOrder.objects.filter(id=contribution_id, order=order).get()
            if contribution.contribution_owner.id == user.id and order.is_open:
                pieces_int = 0
                if pieces:
                    try:
                        pieces_int = int(pieces)
                    except ValueError as ve:
                        logger.error(f'Value error while user try join to order, number of pieces was not integer!'
                                     f'  info: {ve.args}')
                if pieces_int > 0 and ord_type:
                    ContributionOrder.objects.filter(id=contribution_id, order=order).update(
                        number=pieces_int,
                        ord_type=ord_type,
                        add_contr_time=timezone.now(),
                        was_updated=True,
                        description=description
                    )
                    logger.debug(f'User: {user.username} update contribution in order "{hash_id}"! ')
                    return redirect(f'/order/preview-order/{hash_id}/')
                else:
                    context['bad_param'] = 'Bad params!'
                    context['contribution'] = contribution
                    return render(request, 'OrderApp/contribution-update.html', context)
            elif not order.is_open:
                context['bad_param'] = f'Order has been closed at {order.close_time}'
                return render(request, 'TeamPizza/not-authenticated.html', context)
            else:
                return render(request, 'TeamPizza/not-authenticated.html', status=401)
        except DB_Error as db_err:
            logger.error(f'Update order by user {user.username} failed ! info: {db_err.args}')
            context['bad_param'] = 'Not found in data base'
        except BaseException as be:
            logger.error(f'Update order by user {user.username} failed ! Base exception cached info: {be.args}')
            context['bad_param'] = 'Not found in data base'
        return render(request, 'OrderApp/contribution-not-exist.html', context, status=404)
    else:
        context['bad_param'] = 'Bad params! Someone change form!'
        return render(request, 'TeamPizza/operation-failed.html', context, status=400)


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
    context = {'user': user, 'hash_id': hash_id}
    if request.method == 'POST' and user.is_authenticated:
        pieces = ''
        ord_type = ''
        description = ''

        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            pieces = params['pieces']
            ord_type = params['ord_type']
            description = params['description']
        except KeyError as ke:
            logger.error(f'Key error while user try join to order, probably someone change form!'
                         f'  info: {ke.args}')

        db_user: PizzaUser = get_user_from_db(user.username)

        if description == 'Your order description...':
            description = ''

        pieces_int = 0
        if pieces:
            try:
                pieces_int = int(pieces)
            except ValueError as ve:
                logger.error(f'Value error while user try join to order, number of pieces was not integer!'
                             f'  info: {ve.args}')

        if user_already_joined(hash_id, db_user):
            context['bad_param'] = 'You have already joined'
        elif pieces_int > 0 and ord_type and db_user:
            try:
                order = Order.objects.filter(hash_id=hash_id).get()
                actual_time = timezone.now()
                if order.prediction_order_time < actual_time:
                    order = close_after_deadline(hash_id=hash_id)
                contribution = ContributionOrder(
                    contribution_owner=db_user,
                    order=order,
                    number=int(pieces),
                    ord_type=ord_type,
                    add_contr_time=timezone.now(),
                    was_updated=False,
                    description=description
                )
                if order is not None and order.is_open:
                    logger.debug(f'contribution order type before save {contribution.ord_type}')
                    contribution.save()
                    logger.debug(f'contribution order type after save {contribution.ord_type}')
                    logger.debug(f'User: {db_user.username} join to order "{hash_id}"! ')
                    return redirect(f'/order/preview-order/{hash_id}/')
                else:
                    context['bad_param'] = 'This order is closed!'
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
