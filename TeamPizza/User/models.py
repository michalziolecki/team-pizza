from django.db import models


# Main user class
class User(models.Model):
    ADMIN = 'A'
    MODERATOR = 'M'
    USER = 'U'
    ROLES = [
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User')
    ]

    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    mail = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=100)
    role = models.CharField(max_length=1, choices=ROLES, default=USER)


# one to many relation
class LoginInformation(models.Model):
    last_login = models.DateTimeField(null=True)
    ip_login = models.IPAddressField()


# one to one relation
class LastOrder(models.Model):
    pieces_number = models.IntegerField(default=0)
