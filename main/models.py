from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)  # твой хэш
    date_joined = models.DateTimeField(max_length=300)

    def __str__(self):
        return self.username


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    product_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.TextField()
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    count = models.IntegerField()
    product_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class Wishlist(models.Model):
    username = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    product_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
