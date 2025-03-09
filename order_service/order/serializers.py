from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'service_name', 'quantity', 'price']  

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Lấy danh sách các OrderItem của Order

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'total_amount', 'status', 'payment_status', 'shipping_status', 'created_at', 'updated_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')  # Lấy danh sách sản phẩm từ request
        order = Order.objects.create(**validated_data)  # Tạo Order trước

        # Tạo từng OrderItem liên kết với Order
        for item_data in items_data:
            item_serializer = OrderItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save(order=order)

        return order
    
    def update(self, instance, validated_data):
        new_shipping_status = validated_data.get('shipping_status', instance.shipping_status)
        instance = super().update(instance, validated_data)
        if new_shipping_status == "delivered" and instance.status != "completed":
            instance.status = "completed"
            instance.save(update_fields=['status'])
        return instance