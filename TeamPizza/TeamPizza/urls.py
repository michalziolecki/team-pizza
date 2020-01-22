"""TeamPizza URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from .views import home_view, about_view, login_required, operation_success

urlpatterns = [
    path('', home_view, name='index'),
    path('home/', home_view, name='home'),
    path('login-required/', login_required, name='login_required'),
    path('about/', about_view, name='about'),
    path('operation-success/', operation_success, name='success'),
    path('user/', include('UserApp.urls')),
    path('order/', include('OrderApp.urls'))

]
