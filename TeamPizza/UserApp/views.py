from typing import Set, Any, Union

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import logging
from logging import Logger
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from .models import PizzaUser
from django.db import Error as DB_Error
from .user_functions import is_usual_user_and_exist, insert_new_user_into_db, verify_password, \
    update_user_info_while_login, update_user_info_while_logout, get_last_user_login, \
    hash_and_salt_password, get_user_from_db
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import re


def log_form_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'UserApp/login.html', context)


def login_user(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    template = 'UserApp/login.html'
    if request.method == 'POST':
        username = ''
        password = ''
        try:
            username = request.POST['nickname']
            password = request.POST['password']
        except KeyError as ke:
            logger.error(f'Key error while user login, probably some one change form!'
                         f'  info: {ke.args}')
        stored_pwd = ''
        log_user = ''
        if username and password:
            if PizzaUser.objects.filter(username=username).exists():
                log_user = PizzaUser.objects.get(username=username)
                stored_pwd = log_user.password
            elif PizzaUser.objects.filter(email=username).exists():
                log_user = PizzaUser.objects.get(email=username)
                stored_pwd = log_user.password
        if stored_pwd and log_user and verify_password(password=password, stored_password=stored_pwd):
            logger.debug('request for login user and verify password: success')
            update_user_info_while_login(request, log_user)
            login(request, log_user)
            return redirect('/')
        else:
            context['bad_params'] = 'Wrong login or password'
    else:
        template = 'TeamPizza/not-authenticated.html'
    return render(request, template, context)


def logout_user(request: WSGIRequest):
    update_user_info_while_logout(request.user)
    logout(request)
    return redirect('/')


@login_required(login_url='/login-required')
def sign_up_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'UserApp/register.html', context)


@login_required(login_url='/login-required')
def sign_up(request: WSGIRequest) -> HttpResponse:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user: SimpleLazyObject = request.user
    logger.info(f'New user registered by {user.username}, user type: {type(user.username)}')
    context = {'user': user}
    if request.method == 'POST' and user.is_authenticated:
        is_usual, exist = is_usual_user_and_exist(user.username)
        if not is_usual and exist:
            template = insert_new_user_into_db(request, logger)
        else:
            template = 'TeamPizza/not-authenticated.html'

        return render(request, template, context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def account_view(request):
    user = request.user
    login_list = get_last_user_login(user=user)
    context = {
        'user': user,
        'login_list': login_list
    }
    return render(request, 'UserApp/account-view.html', context)


@login_required(login_url='/login-required')
def update_account(request):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}

    if request.method == 'POST' and user.is_authenticated:
        password = ''
        confirmed_password = ''
        old_password = ''

        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            password = params['password']
            confirmed_password = params['confirm_password']
            old_password = params['old_password']
        except KeyError as ke:
            logger.error(f'Key error while user try change password, probably someone change form!'
                         f'  info: {ke.args}')

        db_user = get_user_from_db(user.username)
        pwd_regex = re.compile('.{9,}')

        if old_password and verify_password(old_password, db_user.password):
            if password and confirmed_password and password == confirmed_password and pwd_regex.match(password):
                password_hash = hash_and_salt_password(password)
                try:
                    PizzaUser.objects.filter(username=user.username).update(password=password_hash)
                    logger.info(f'Password for user "{user.username}" changed')
                    return redirect('/operation-success/')
                except DB_Error as db_err:
                    logger.error(f'Update user password field failed ! info: {db_err.args}')
                    context['bad_pwd_params'] = 'Problem with database try again'
                except BaseException as be:
                    logger.error(f'Update user password field failed! Base exception cached info: {be.args}')
                    context['bad_pwd_params'] = 'Problem with database try again'
            else:
                context["bad_pwd_params"] = 'Password is incorrect'
        else:
            context['bad_pwd_params'] = 'Password is incorrect'

        return render(request, 'UserApp/account-view.html', context)

    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def remove_account(request):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}

    if request.method == 'POST' and user.is_authenticated:
        remove = False
        password = ''
        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            remove = params['removeCheckbox']
            logger.debug(f'remove field type: {type(remove)}, status: {remove}')
            password = params['password']
        except KeyError as ke:
            logger.error(f'Key error while user try remove account, probably someone change form!'
                         f'  info: {ke.args}')

        db_user = get_user_from_db(user.username)

        if password and verify_password(password, db_user.password) and remove:
            try:
                PizzaUser.objects.filter(username=user.username).delete()
                logger.info(f'User "{user.username}" removed from database')
                # logout operation after removed account
                logout(request)
                return redirect('/operation-success/')
            except DB_Error as db_err:
                logger.error(f'Update user password field failed ! info: {db_err.args}')
                context['bad_rm_params'] = 'Problem with database try again'
            except BaseException as be:
                logger.error(f'Update user password field failed! Base exception cached info: {be.args}')
                context['bad_rm_params'] = 'Problem with database try again'
        else:
            if remove:
                context['bad_rm_params'] = 'Password is incorrect'
            else:
                context['bad_rm_params'] = 'Account not removed'

        return render(request, 'UserApp/account-view.html', context)

    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)
