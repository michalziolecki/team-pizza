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
    update_user_info_while_login, update_user_info_while_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


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
        logger.debug(f'request dict: {request.POST}')
        try:
            username = request.POST['nickname']
            password = request.POST['password']
        except KeyError as ke:
            logger.error('Key error while user login, probably some one change form!'
                         '  info: {}'.format(ke.args))
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
            logger.debug(f'request for login user and verify password: success')
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
    logger.debug(f'POST headers: {request.headers}')
    logger.debug(f'POST body: {request.body}')

    context = {'user': user}
    if request.method == 'POST' and user.is_authenticated:
        is_usual, exist = is_usual_user_and_exist(user.username)
        if not is_usual and exist:
            template = insert_new_user_into_db(request, logger)
        else:
            template = 'TeamPizza/not-authenticated.html'

        return render(request, template, context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context)
    else:
        return render(request, 'TeamPizza/bad-method.html', context)


@login_required(login_url='/login-required')
def account_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'UserApp/account-view.html', context)


@login_required(login_url='/login-required')
def account_security_view(request):
    pass


@login_required(login_url='/login-required')
def update_account(request):
    pass


@login_required(login_url='/login-required')
def delete_account(request):
    pass


@login_required(login_url='/login-required')
def security_account(request):
    pass
