from django.contrib import admin
from .models import Product, Cart, Wishlist, Category

# 1. Простой способ регистрации
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Category)