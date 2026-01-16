from django.db import models
from django.contrib.auth.models import User
import json

class Account(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)  # твой хэш
    date_joined = models.DateTimeField(max_length=300)

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='childrem'
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    product_id = models.IntegerField(null=True, blank=True)
    wishlist = models.BooleanField(default=False)
    description = models.TextField(default='', max_length=2000)
    default_category = ""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_DEFAULT,  # Устанавливаем значение по умолчанию при удалении
        default=default_category,
        null=True,  # Разрешить NULL для существующих записей
        blank=True,
        # ID дефолтной категории
        related_name='products'
    )

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


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('pending_capture', 'Ожидает подтверждения'),
        ('completed', 'Оплачен'),
        ('failed', 'Неудачный'),
        ('canceled', 'Отменен'),
    ]

    user = models.CharField(max_length=100)
    total_amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    items = models.TextField()  # JSON с товарами
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_items(self):
        return json.loads(self.items) if self.items else []

    def __str__(self):
        return f"Order #{self.id} - {self.user} - {self.total_amount} RUB"


