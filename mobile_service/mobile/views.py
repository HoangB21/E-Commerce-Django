from rest_framework import viewsets
from .models import MobileDevice
from .serializers  import MobileDeviceSerializer
import logging

logger = logging.getLogger(__name__)

class MobileDeviceViewSet(viewsets.ModelViewSet):
    queryset = MobileDevice.objects.all()
    serializer_class = MobileDeviceSerializer

    def perform_create(self, serializer):
        serializer.save()
        logger.info(f"Mobile device created: {serializer.data['name']}")

    def perform_update(self, serializer):
        serializer.save()
        logger.info(f"Mobile device updated: {serializer.data['name']}")

    def perform_destroy(self, instance):
        logger.info(f"Mobile device deleted: {instance.name}")
        instance.delete()