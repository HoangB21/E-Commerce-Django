from rest_framework import serializers
from .models import Payment, PaymentItem

class PaymentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentItem
        fields = ["product_id", "product_name", "service_name", "quantity", "price"]

class PaymentSerializer(serializers.ModelSerializer):
    items = PaymentItemSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "order_id", "amount", "status", "method", "created_at", "items"]
