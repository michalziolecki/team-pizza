from django.urls import path
from .views import log_form_view, login, sign_up, sign_up_view

urlpatterns = [
    path('login/', login),
    path('log-form/', log_form_view),
    path('sign-up/', sign_up),
    path('sign-up-form/', sign_up_view)
]