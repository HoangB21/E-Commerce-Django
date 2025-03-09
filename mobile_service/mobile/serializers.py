from rest_framework import serializers
from .models import MobileDevice

class MobileDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileDevice
        fields = [
            'id', 'name', 'brand', 'price', 'stock', 'image', 'service',
            'screen_size', 'ram', 'storage', 'camera', 'created_at', 'updated_at'
        ]

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value