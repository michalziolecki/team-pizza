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


class LoginInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True)
    ip_login = models.GenericIPAddressField()


class LastOrder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pieces_number = models.IntegerField(default=0)
