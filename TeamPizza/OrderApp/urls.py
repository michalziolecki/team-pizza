from django.urls import path
from .views import order_options_view, create_order, join_order, close_order, delete_order, \
    opened_order_view, join_order_view

urlpatterns = [
    path('options/', order_options_view),
    path('create/', create_order),
    path('join-to-order/<str:hash_id>/', join_order_view),
    path('preview-order/<str:hash_id>/', opened_order_view),
    path('join/<int:hash_id>/', join_order),
    path('close/', close_order),
    path('delete/', delete_order)
]
