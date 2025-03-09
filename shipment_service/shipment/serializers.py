from rest_framework import serializers
from .models import Shipment, ShipmentStatusHistory

class ShipmentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentStatusHistory
        fields = ['status', 'changed_at', 'note']

class ShipmentSerializer(serializers.ModelSerializer):
    status_history = ShipmentStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = ['order_id', 'status', 'created_at', 'updated_at', 'tracking_number', 'estimated_delivery', 'status_history']