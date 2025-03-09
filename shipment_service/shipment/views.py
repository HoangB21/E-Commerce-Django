import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipment, ShipmentStatusHistory
from .serializers import ShipmentSerializer
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

# Tạo shipment
class ShipmentCreateView(APIView):
    def post(self, request):
        serializer = ShipmentSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                shipment = serializer.save()
                # Ghi lịch sử trạng thái ban đầu
                ShipmentStatusHistory.objects.create(
                    shipment=shipment,
                    status=shipment.status
                )
                logger.info("Shipment created for order_id %s with status %s", shipment.order_id, shipment.status)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Failed to create shipment: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Xem chi tiết shipment
class ShipmentDetailView(APIView):
    def get(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            serializer = ShipmentSerializer(shipment)
            logger.info("Shipment details fetched for order_id %s", order_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Shipment.DoesNotExist:
            logger.warning("Shipment not found for order_id %s", order_id)
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

# Cập nhật trạng thái shipment
class ShipmentUpdateView(APIView):
    def patch(self, request, order_id):
        try:
            shipment = Shipment.objects.get(order_id=order_id)
            old_status = shipment.status
            serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()
                    if old_status != serializer.validated_data['status']:
                        ShipmentStatusHistory.objects.create(
                            shipment=shipment,
                            status=serializer.validated_data['status'],
                            note=request.data.get('note', None)
                        )
                    logger.info("Shipment updated for order_id %s to status %s", order_id, serializer.data['status'])

                    # Gọi API đến order_service
                    order_service_url = f"http://127.0.0.1:7001/api/orders/{order_id}/"
                    order_payload = {"shipping_status": serializer.validated_data['status']}
                    response = requests.patch(order_service_url, json=order_payload, timeout=5)
                    if not response.ok:  # Kiểm tra lỗi
                        logger.error("Failed to update order_service: %s", response.text)
                        raise Exception("Failed to sync with order_service")
                    
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Shipment.DoesNotExist:
            logger.warning("Shipment not found for order_id %s", order_id)
            return Response({"error": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error in shipment update for order_id %s: %s", order_id, str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)