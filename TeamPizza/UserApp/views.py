from typing import Set, Any, Union

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import logging
from logging import Logger
from django.core.handlers.wsgi import WSGIRequest
from django.utils.functional import SimpleLazyObject
from django.http.request import QueryDict
from .models import PizzaUser, ConfirmAccount, RestorePassword
from django.db import Error as DB_Error
from django.contrib.auth.tokens import default_token_generator
from .user_functions import is_usual_user_and_exist, insert_new_user_into_db, verify_password, \
    update_user_info_while_login, update_user_info_while_logout, get_last_user_login, \
    hash_and_salt_password, get_user_from_db, is_root_by_role, get_user_from_db_by_mail, create_token_to_restore_pwd
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from smtplib import SMTPAuthenticationError
from django.utils import timezone
from TeamPizza.settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD

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
        if stored_pwd and log_user:
            if verify_password(password=password, stored_password=stored_pwd) \
                    and log_user.is_active:
                logger.debug('request for login user and verify password: success')
                update_user_info_while_login(request, log_user)
                login(request, log_user)
                return redirect('/')
            elif not log_user.is_active:
                context['bad_params'] = 'Confirm Your account by email!'
            else:
                context['bad_params'] = 'Wrong login or password!'
        else:
            context['bad_params'] = 'Wrong login or password!'
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


def self_sign_up_view(request: WSGIRequest):
    user = request.user
    context = {'user': user}
    return render(request, 'UserApp/register.html', context)


@login_required(login_url='/login-required')
def sign_up(request: WSGIRequest) -> HttpResponse:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user: SimpleLazyObject = request.user
    context = {'user': user}
    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        selected_role = params['role']
        username = params['nickname']
        mail = params['mail']
        password = params['password']
    except KeyError as ke:
        logger.error(f'Sign up method failed while parsing params! info -> params: {params},'
                     f' user: {user.username}, dict exception info: {ke.args}')
        return render(request, 'TeamPizza/bad-method.html', context, status=400)

    if selected_role == 'R' and not is_root_by_role(user.role):
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)

    mail_regex = re.compile('^.*@teldat\.com\.pl$')
    correct_mail = mail_regex.match(mail)

    if request.method == 'POST' and user.is_authenticated and user.role != 'U' and correct_mail:
        is_usual, exist = is_usual_user_and_exist(user.username)
        if not is_usual and exist:
            template, confirm_token = insert_new_user_into_db(request, logger)
            logger.info(f'New user registered by {user.username}')
            new_user = get_user_from_db(username)
            if new_user and confirm_token:
                logger.info(f'New user registered - his/her email: {mail}')
                subject = 'Hello ! Welcome on pizza.teldat portal!'
                message = f'This is verifying message. \n' \
                          f'Your temporary password is: "{password}" - remember to change this password!' \
                          f'click this link or copy into browser: \n' \
                          f'https://teldat.pizza/user/confirm/{username}/{confirm_token}/'
                recipient = new_user.email
                try:
                    send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=False)
                    context['params'] = 'New user must to confirm email'
                    template = 'UserApp/sign-up-success.html'
                except SMTPAuthenticationError as smtp_err:
                    logger.error(f'SMTPAuthenticationError while sending email, info: user - {user.username},'
                                 f' email - {recipient}. What: {smtp_err.args} ')
                    context['email'] = recipient
                    template = 'UserApp/sending-email-error.html'
                except BaseException as be:
                    logger.error(f'BaseException while sending email, info: user - {user.username},'
                                 f' email - {recipient}. What: {be.args} ')
                    context['email'] = recipient
                    template = 'UserApp/sending-email-error.html'

            return render(request, template, context)
        else:
            template = 'TeamPizza/not-authenticated.html'

        return render(request, template, context)
    elif not user.is_authenticated or user.role == 'U' or not correct_mail:
        if not correct_mail:
            context['bad_param'] = 'Incorrect mail domain'
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


def self_sign_up(request: WSGIRequest) -> HttpResponse:
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user: SimpleLazyObject = request.user
    context = {'user': user}
    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        selected_role = params['role']
        mail = params['mail']
        username = params['nickname']
    except KeyError as ke:
        logger.error(f'Sign up method failed while parsing params!'
                     f' user: {user.username}, dict exception info: {ke.args}')
        return render(request, 'TeamPizza/bad-method.html', context, status=400)

    mail_regex = re.compile('^.*@teldat\.com\.pl$')  # '.*'
    correct_mail = mail_regex.match(mail)

    if request.method == 'POST' and selected_role == 'U' and correct_mail:
        template, confirm_token = insert_new_user_into_db(request, logger)
        new_user = get_user_from_db(username)
        if new_user and confirm_token:
            logger.info(f'New user registered - his/her email: {mail}')
            subject = 'Hello ! Welcome on pizza.teldat portal!'
            message = f'This is verifying message. \n' \
                      f'click this link or copy into browser: \n' \
                      f'https://teldat.pizza/user/confirm/{username}/{confirm_token}/'
            recipient = new_user.email
            try:
                send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=False)
                return redirect('/confirm-email/')
            except SMTPAuthenticationError as smtp_err:
                logger.error(f'SMTPAuthenticationError while sending email, info: user - {user.username},'
                             f' email - {recipient}. What: {smtp_err.args} ')
                context['email'] = recipient
                template = 'UserApp/sending-email-error.html'
            except BaseException as be:
                logger.error(f'BaseException while sending email, info: user - {user.username},'
                             f' email - {recipient}. What: {be.args} ')
                context['email'] = recipient
                template = 'UserApp/sending-email-error.html'
        return render(request, template, context)
    elif selected_role != 'U' or not correct_mail:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


def confirm_mail_by_token(request: WSGIRequest, nickname, token: str):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    context = {}
    if request.method == 'GET' and nickname and token:
        user = get_user_from_db(nickname)
        confirm = ''
        if user:
            try:
                confirm = ConfirmAccount.objects.filter(user=user, token=token).get()
            except DB_Error as db_err:
                logger.error(f'Confirm account by token, failed ! info: {db_err.args}')
            except BaseException as be:
                logger.error(f'Confirm account by token, failed ! Base exception cached info: {be.args}')
        if confirm and confirm.deadline > timezone.now():
            try:
                PizzaUser.objects.filter(id=user.id, username=user.username).update(is_active=True)
                confirm.delete()
                context['data'] = 'Account confirmed'
            except DB_Error as db_err:
                logger.error(f'Activate account and remove confirm token, failed ! info: {db_err.args}')
                context['data'] = 'Account activation failed ! \n Contact with admin or try again.'
            except BaseException as be:
                logger.error(
                    f'Activate account and remove confirm token, failed ! Base exception cached info: {be.args}')
                context['data'] = 'Account activation failed ! \n Contact with admin or try again.'
        elif confirm and confirm.deadline <= timezone.now():
            context['data'] = 'Link has expired'
        else:
            context['data'] = 'Link not exist'
        return render(request, 'UserApp/confirm-by-token.html', context)
    elif not token:
        return render(request, 'TeamPizza/not-found.html', context, status=404)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


def send_mail_to_restore_pwd_view(request: WSGIRequest):
    return render(request, 'UserApp/send-mail-to-restore-pwd.html')


def send_mail_to_restore_pwd(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    context = {}
    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        mail = params['email']
    except KeyError as ke:
        logger.error(f'send_mail_to_restore_pwd method failed while parsing params!'
                     f' dict exception info: {ke.args}')
        return render(request, 'TeamPizza/bad-method.html', status=400)

    mail_regex = re.compile('^.*@teldat\.com\.pl$')  #
    correct_mail = mail_regex.match(mail)

    if request.method == 'POST' and correct_mail:
        restored_user = get_user_from_db_by_mail(mail)
        init_token, confirm_token = create_token_to_restore_pwd(restored_user)
        # template, confirm_token = insert_new_user_into_db(request, logger)
        if restored_user and init_token and confirm_token:
            logger.info(f'User with email: {mail}, try to restore password')
            subject = 'Restore password to pizza.teldat portal!'
            message = f'Restore password: \n' \
                      f'- to restore password, click on this link or copy into browser: \n' \
                      f'https://teldat.pizza/user/restore-user-pwd/{restored_user.username}/{confirm_token}/'
            try:
                send_mail(subject, message, EMAIL_HOST_USER, [mail], fail_silently=False)
                return redirect('/confirm-email/')
            except SMTPAuthenticationError as smtp_err:
                logger.error(f'SMTPAuthenticationError while sending email, info: user - {restored_user.username},'
                             f' email - {mail}. What: {smtp_err.args} ')
                context['email'] = mail
                template = 'UserApp/sending-email-error.html'
            except BaseException as be:
                logger.error(f'BaseException while sending email, info: user - {restored_user.username},'
                             f' email - {mail}. What: {be.args} ')
                context['email'] = mail
                template = 'UserApp/sending-email-error.html'
        elif not init_token and restored_user:
            template = 'UserApp/sending-email-error.html'
            logger.error(f'Problem with creating token to restore password for user: {restored_user.username}')
        else:
            return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
        return render(request, template, context)
    elif not correct_mail:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


def restore_password_view(request: WSGIRequest, nickname: str, token: str):
    context = {
        'username': nickname,
        'token': token
    }
    return render(request, 'UserApp/restore-password-view.html', context)


def restore_password(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    context = {}
    try:
        post_body: QueryDict = request.POST
        params: dict = post_body.dict()
        username = params['username']
        token = params['token']
        password = params['password']
        confirm_password = params['confirm_password']
    except KeyError as ke:
        logger.error(f'send_mail_to_restore_pwd method failed while parsing params!'
                     f' dict exception info: {ke.args}')
        return render(request, 'TeamPizza/bad-method.html', status=400)

    if request.method == 'POST' and token and password and confirm_password:
        template = 'UserApp/confirm-by-token.html'
        status = 200
        restored_user = get_user_from_db(username)
        if restored_user:
            restore_pwd_token = ''
            try:
                restore_pwd_token = RestorePassword.objects.filter(user=restored_user, token=token).get()
            except DB_Error as db_err:
                logger.error(f'Restore password by token, failed ! info: {db_err.args}')
            except BaseException as be:
                logger.error(f'Restore password by token, failed ! Base exception cached info: {be.args}')
            if restore_pwd_token and restore_pwd_token.deadline > timezone.now():
                if password == confirm_password:
                    hash_pwd = hash_and_salt_password(password)
                    try:
                        PizzaUser.objects \
                            .filter(id=restored_user.id,
                                    username=restored_user.username)\
                            .update(password=hash_pwd)
                        restore_pwd_token.delete()
                        return redirect('/operation-success/')
                    except DB_Error as db_err:
                        logger.error(f'Activate account and remove confirm token, failed ! info: {db_err.args}')
                        context['data'] = 'Account activation failed ! \n Contact with admin or try again.'
                    except BaseException as be:
                        logger.error(
                            f'Activate account and remove confirm token, failed ! Base exception cached info: {be.args}')
                        context['data'] = 'Account activation failed ! \n Contact with admin or try again.'
                else:
                    template = 'UserApp/restore-password-view.html'
                    status = 304
                    context['bad_param'] = 'Password are not the same'
            elif restore_pwd_token and restore_pwd_token.deadline <= timezone.now():
                context['data'] = 'Link has expired'
                template = 'UserApp/confirm-by-token.html'
                status = 404
            else:
                template = 'TeamPizza/not-found.html'
                status = 404
        else:
            template = 'TeamPizza/not-found.html'
            status = 404
        return render(request, template, context, status=status)
    elif not token:
        return render(request, 'TeamPizza/not-found.html', context, status=404)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def account_view(request: WSGIRequest):
    user = request.user
    login_list = get_last_user_login(user=user)
    context = {
        'user': user,
        'login_list': login_list
    }
    return render(request, 'UserApp/account-view.html', context)


@login_required(login_url='/login-required')
def update_account(request: WSGIRequest):
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
def remove_account(request: WSGIRequest):
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


@login_required(login_url='/login-required')
def users_view(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    user = request.user
    context = {'user': user}
    if request.method == "GET" and user.is_authenticated:
        try:
            context['users_list'] = PizzaUser.objects.all()
        except DB_Error as db_err:
            logger.error(f'Get all users from db failed ! info: {db_err.args}')
            context['bad_param'] = 'Problem with database try again'
        except BaseException as be:
            logger.error(f'Get all users from db failed! Base exception cached info: {be.args}')
            context['bad_param'] = 'Problem with database try again'
        return render(request, 'UserApp/users.html', context)
    elif not user.is_authenticated:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)


@login_required(login_url='/login-required')
def change_privileges(request: WSGIRequest):
    logger: Logger = logging.getLogger(settings.LOGGER_NAME)
    admin_user = request.user
    context = {'user': admin_user}
    role_value = {'R': 0, 'A': 1, 'M': 2, 'U': 3}

    def confirm_update_privileges(update_user: PizzaUser, admin: PizzaUser, role_new: str) -> bool:
        confirm = True
        if update_user.role == 'R':
            confirm = False
        if role_value[updating_user.role] <= role_value[admin.role]:
            confirm = False
        if role_value[role_new] < role_value[admin.role]:
            confirm = False

        return confirm

    if request.method == "POST" and admin_user.is_authenticated and role_value[admin_user.role] <= 1:
        user_id = ''
        username = ''
        new_role = ''
        try:
            post_body: QueryDict = request.POST
            params: dict = post_body.dict()
            user_id = params['id']
            username = params['nickname']
            new_role = params['role']
        except KeyError as ke:
            logger.error(f'Key error while admin {admin_user.username} try update role of user {username}, '
                         f'probably someone change form! info: {ke.args}')

        if user_id and username and new_role:
            updating_user: PizzaUser = get_user_from_db(username)
            if confirm_update_privileges(updating_user, admin_user, new_role):
                try:
                    PizzaUser.objects.filter(username=updating_user.username).update(role=new_role)
                    return redirect('/user/users/')
                except DB_Error as db_err:
                    logger.error(f'Update user password field failed ! info: {db_err.args}')
                    context['bad_param'] = 'Problem with database while updating - try again!'
                except BaseException as be:
                    logger.error(f'Update user password field failed! Base exception cached info: {be.args}')
                    context['bad_param'] = 'Problem with database while updating - try again!'
                return render(request, 'TeamPizza/operation-failed.html', context, status=500)
            else:
                return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    elif not admin_user.is_authenticated or role_value[admin_user.role] <= 1:
        return render(request, 'TeamPizza/not-authenticated.html', context, status=401)
    else:
        return render(request, 'TeamPizza/bad-method.html', context, status=400)
