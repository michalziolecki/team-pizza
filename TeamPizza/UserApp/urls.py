from django.urls import path
from .views import log_form_view, login_user, sign_up, sign_up_view, logout_user, \
    account_view, update_account, remove_account, users_view, change_privileges, self_sign_up_view,\
    self_sign_up, confirm_mail_by_token, send_mail_to_restore_pwd_view, send_mail_to_restore_pwd, \
    restore_password_view, restore_password

urlpatterns = [
    path('login/', login_user),
    path('log-form/', log_form_view),
    path('logout/', logout_user),
    path('sign-up/', sign_up),
    path('sign-up-form/', sign_up_view),
    path('self-sign-up/', self_sign_up),
    path('self-sign-up-form/', self_sign_up_view),
    path('confirm/<str:nickname>/<str:token>/', confirm_mail_by_token),
    path('mail-restore-pwd/', send_mail_to_restore_pwd_view),
    path('mail-restore-pwd-send/', send_mail_to_restore_pwd),
    path('restore-user-pwd/<str:nickname>/<str:token>/', restore_password_view),
    path('restore-pwd/', restore_password),
    path('account/', account_view),
    path('update-account/', update_account),
    path('remove-account/', remove_account),
    path('change-privileges/', change_privileges),
    path('users/', users_view)
]
