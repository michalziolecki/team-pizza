from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def log_form_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/login.html', context)


def login(request):
    user = request.user
    context = {'user': user}
    # method to login user
    return render(request, 'TeamPizza/index.html', context)


@login_required(login_url='/login-required')
def sign_up_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/register.html', context)


@login_required(login_url='/login-required')
def sign_up(request):
    user = request.user
    context = {'user': user}
    # method to add user
    return render(request, 'User/index.html', context)
