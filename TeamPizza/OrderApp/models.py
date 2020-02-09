from django.conf import settings
from django.db import models
from hashid_field import HashidField


class Order(models.Model):
    hash_id = models.CharField(max_length=40, null=False, unique=True)
    order_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prediction_order_time = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True)
    is_open = models.BooleanField(default=True, null=False)
    open_time = models.DateTimeField(null=False)
    close_time = models.DateTimeField(null=True)  # while migration comment and next uncomment


class ContributionOrder(models.Model):
    SMALL = 'S'
    BIG = 'B'
    ROLES = [
        (SMALL, 'small'),
        (BIG, 'big')
    ]
    contribution_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pieces_number = models.IntegerField(null=False)
    size = models.CharField(max_length=1, choices=ROLES, default=BIG)
    add_contr_time = models.DateTimeField(null=False)
    was_updated = models.BooleanField(default=False)
    description = models.CharField(max_length=200)
