from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import logging
from logging import Logger
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from .models import User
from django.db import Error as DB_Error
from .user_functions import is_usual_user_and_exist, hash_and_salt_password
from django.contrib.auth.decorators import login_required


def log_form_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'User/login.html', context)


def login(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    # method to login user
    return render(request, 'TeamPizza/index.html', context)


# @login_required(login_url='/login-required')
def sign_up_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'User/register.html', context)


# @login_required(login_url='/login-required')
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
            template = insert_into_db(request, logger)
        else:
            template = 'TeamPizza/not-authenticated.html'

        return render(request, template, context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context)
    else:
        return render(request, 'TeamPizza/bad-method.html', context)


def insert_into_db(request: WSGIRequest, logger: Logger) -> str:
    user = request.user
    post_body: QueryDict = request.POST
    params: dict = post_body.dict()
    template = 'sign-up-success.html'

    # TODO hash password
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
