from django.contrib import admin
from .models import Product, Cart, Wishlist, Category


admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(Category)