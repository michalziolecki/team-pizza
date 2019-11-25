from django.shortcuts import render


def log_form_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/login.html', context)


def login_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'User/login.html', context)
