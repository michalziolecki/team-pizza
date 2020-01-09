from django.urls import path
from .views import order_options_view, create_order, make_order, close_order, delete_order, opened_order_view

urlpatterns = [
    path('options/', order_options_view),
    path('opened/', opened_order_view),
    path('create/', create_order),
    path('make/', make_order),
    path('close/', close_order),
    path('delete/', delete_order)
]
