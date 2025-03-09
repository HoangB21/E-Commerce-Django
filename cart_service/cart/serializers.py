from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'service_name', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)  # Hiển thị danh sách sản phẩm trong giỏ hàng

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'created_at', 'items']