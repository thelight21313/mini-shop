from django.db import models
from django.contrib.auth.models import User
import json


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
#    default_category, _ = Category.objects.get_or_create(
#        name="all",
#        defaults={'parent': None}
#    )

    category = models.ForeignKey(
        Category,
#        default=default_category.id,  # ID дефолтной категории
        blank=True,
        null=True,
        related_name='products'
    )

    def __str__(self):
        return self.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    image_url = models.CharField(max_length=500)
    count = models.IntegerField()
    product_id = models.IntegerField(null=True, blank=True)
    item_total = models.IntegerField()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.item_total = self.price * self.count
        super().save(*args, **kwargs)

    def increase_quantity(self, amount=1):
        self.count += amount
        self.save()
        return self

    def reduce_quantity(self, amount=1):
        if self.count > amount:
            self.count -= amount
            self.save()
        else:
            self.delete()

    def count_for_user(self, user):
        return self.objects.filter(user=user).count()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
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


