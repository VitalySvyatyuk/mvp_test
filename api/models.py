from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller')
    ]

    email = models.EmailField('email address', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, null=True, blank=True)
    deposit = models.IntegerField(default=0)

    REQUIRED_FIELDS = []


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    amount_available = models.IntegerField(default=0)
    cost = models.IntegerField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
