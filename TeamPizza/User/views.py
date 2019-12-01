from django.shortcuts import render
from django.conf import settings
import logging
from logging import Logger
from django.core.handlers.wsgi import WSGIRequest
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
def sign_up(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    logger.info(type(request))
    logger.info(type(logger))
    # method to add user
    # if request.method
    return render(request, 'User/index.html', context)
