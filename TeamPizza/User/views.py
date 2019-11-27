from django.shortcuts import render


def log_form_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/login.html', context)


def login(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/index.html', context)


def sign_up_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/register.html', context)


def sign_up(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/index.html', context)
