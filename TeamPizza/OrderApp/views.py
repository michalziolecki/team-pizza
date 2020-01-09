from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login-required')
def order_options_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'OrderApp/order-options-view.html', context)


@login_required(login_url='/login-required')
def opened_order_view(request):
    user = request.user
    context = {'user': user}
    return render(request, 'OrderApp/order-options-view.html', context)


@login_required(login_url='/login-required')
def create_order(request):
    user = request.user
    context = {'user': user}
    # POST method to create order in db
    return render(request, 'OrderApp/order-options-view.html', context)


@login_required(login_url='/login-required')
def make_order(request):
    user = request.user
    context = {'user': user}
    # POST method to add preferences to order in db
    return render(request, 'OrderApp/order-options-view.html', context)


@login_required(login_url='/login-required')
def close_order(request):
    user = request.user
    context = {'user': user}
    # POST method to close order in db
    return render(request, 'OrderApp/order-closed.html', context)


@login_required(login_url='/login-required')
def delete_order(request):
    user = request.user
    context = {'user': user}
    # POST method to delete order in db
    return render(request, 'OrderApp/order-deleted.html', context)
