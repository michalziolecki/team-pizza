from django.urls import path
from .views import log_form_view, login_view

urlpatterns = [
    path('login/', login_view),
    path('log-form/', log_form_view),
]