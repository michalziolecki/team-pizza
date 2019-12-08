from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserDjango
from .models import PizzaUser

# Register your models here.
admin.site.register(PizzaUser, UserDjango)
