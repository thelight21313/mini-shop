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
    wishlist = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.TextField()
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    count = models.IntegerField()
    product_id = models.IntegerField(null=True, blank=True)
    item_total = models.IntegerField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматически пересчитываем перед сохранением в базу
        self.item_total = self.price * self.count
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    username = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    product_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
