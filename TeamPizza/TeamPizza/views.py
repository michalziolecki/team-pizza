from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/index.html', context)


# @login_required(login_url='/login-required')
def about_view(request):
    return render(request, 'TeamPizza/about.html')


# @login_required(login_url='/login-required')
def operation_success(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/operation-success.html', context)


def confirm_email(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/confirm-signup.html', context)


# @login_required(login_url='/login-required')
def operation_failed(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/operation-failed.html', context)


def login_required(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/login-required.html', context)
