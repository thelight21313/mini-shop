import django
from django.conf import settings
from datetime import datetime
from pathlib import Path
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from .models import Cart, Product


class CounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['user', 'title', 'price', 'image_url', 'count', 'product_id', 'item_total']

    def get_item_total(self, obj):
        return obj.price * obj.count


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'price', 'image_url', 'product_id', 'wishlist']


class ProductserForUpdatePage(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'price', 'image_url', 'product_id', 'in_wishlist']
        read_only_fields = ['in_wishlist']
    def get_in_wishlist(self, obj):
        wishlist_ids = self.context.get('wishlist_ids', [])
        return obj.product_id in wishlist_ids
