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
from .user_functions import is_usual_user_and_exist, insert_new_user_into_db
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
            template = insert_new_user_into_db(request, logger)
        else:
            template = 'TeamPizza/not-authenticated.html'

        return render(request, template, context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context)
    else:
        return render(request, 'TeamPizza/bad-method.html', context)



