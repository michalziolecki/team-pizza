from django.urls import path
from .views import order_options_view, create_order, join_order, close_order, delete_order, \
    opened_order_view, join_order_view, delete_contribution, update_contribution, update_order_view

urlpatterns = [
    path('options/', order_options_view),
    path('create/', create_order),
    path('preview-order/<str:hash_id>/', opened_order_view),
    path('join-to-order/<str:hash_id>/', join_order_view),
    path('join/<str:hash_id>/', join_order),
    path('update/<str:hash_id>/', update_order_view),
    path('close/<str:hash_id>/', close_order),
    path('delete/<str:hash_id>/', delete_order),
    path('update-contribution/<str:hash_id>/<str:contribution_id>/', update_contribution),
    path('delete-contribution/<str:hash_id>/<str:contribution_id>/', delete_contribution)
]
