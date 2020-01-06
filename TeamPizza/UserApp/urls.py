from django.urls import path
from .views import log_form_view, login_user, sign_up, sign_up_view, logout_user, account_view

urlpatterns = [
    path('login/', login_user),
    path('log-form/', log_form_view),
    path('logout/', logout_user),
    path('sign-up/', sign_up),
    path('sign-up-form/', sign_up_view),
    path('account/', account_view)
]
