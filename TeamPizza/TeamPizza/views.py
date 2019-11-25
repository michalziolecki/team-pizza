from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/index.html', context)


# @login_required
def about_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'TeamPizza/about.html', context)
