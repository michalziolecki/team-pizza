from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# Main user class
class PizzaUser(AbstractUser):
    ROOT = 'R'
    ADMIN = 'A'
    MODERATOR = 'M'
    USER = 'U'
    ROLES = [
        (ROOT, 'Root'),
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'UserApp')
    ]

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=572)
    role = models.CharField(max_length=1, choices=ROLES, default=USER)


class LoginInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True)
    ip_login = models.GenericIPAddressField()


class LastOrder(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pieces_number = models.IntegerField(default=0)
