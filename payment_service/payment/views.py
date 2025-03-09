import requests
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from .models import Payment, PaymentItem
from .serializers import PaymentSerializer
import logging

logger = logging.getLogger(__name__)

class PaymentDetailView(APIView):
    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
            serializer = PaymentSerializer(payment)
            logger.info("Payment details fetched for order_id %s", order_id)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            logger.warning("Payment not found for order_id %s", order_id)
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error fetching payment for order_id %s: %s", order_id, str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InitiatePaymentView(APIView):
    def post(self, request):
        # Lấy order_id trực tiếp từ request.data
        order_id = request.data.get('order_id')
        print(order_id)
        if not order_id:
            return Response({"error": "order_id is required"}, 
                          status=status.HTTP_400_BAD_REQUEST)

        # Gọi API tới order_service để lấy thông tin đơn hàng
        order_service_url = f"http://127.0.0.1:7001/api/orders/{order_id}/"
        try:
            response = requests.get(order_service_url)
            response.raise_for_status()  # Ném lỗi nếu request thất bại
            order_data = response.json()
            total_amount = order_data.get('total_amount')
            if not total_amount:
                return Response({"error": "Total amount not found in order data"}, 
                              status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to fetch order details: {str(e)}"}, 
                          status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Cấu hình PayPal form
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": str(total_amount),
            "item_name": f"Order #{order_id}",
            "invoice": order_id,
            "currency_code": "USD",
            "notify_url": "https://6b1f-2a09-bac1-7a80-50-00-246-5b.ngrok-free.app/api/payments/paypal-ipn/",
            "return_url": "http://127.0.0.1:9000/payment/success/",
            "cancel_return": "http://127.0.0.1:9000/payment/cancel/",
        }
    
        form = PayPalPaymentsForm(initial=paypal_dict)
        return Response({
            "message": "Payment initiated",
            "paypal_form": form.render()
        }, status=status.HTTP_200_OK)
    
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    print("paypal_payment_received")
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        order_id = ipn_obj.invoice
        
        # Công việc 1: Tạo Payment và PaymentItem
        success_1, message_1 = create_payment_from_order(order_id)
        if not success_1:
            logger.error(message_1)
            return
        
        # Công việc 2: Cập nhật payment_status trong order_service
        success_2, message_2 = update_order_payment_status(order_id)
        if not success_2:
            logger.error(message_2)
            return
        
        # Công việc 3: Gọi API tạo shipment
        shipment_data = {"order_id": order_id, "status": "waiting"}
        try:
            response = requests.post("http://127.0.0.1:7003/api/shipments/create/", json=shipment_data)
            response.raise_for_status()
            logger.info("Shipment created for order %s", order_id)
        except requests.exceptions.RequestException as e:
            logger.error("Failed to create shipment for order %s: %s", order_id, str(e))
        
        logger.info(f"Payment completed and processed for order {order_id}")
    else:
        logger.info(f"Payment status for order {ipn_obj.invoice}: {ipn_obj.payment_status}")

def create_payment_from_order(order_id):
    # URL API của order_service
    order_service_url = f"http://127.0.0.1:7001/api/orders/detail/{order_id}/"
    
    try:
        # Gọi API để lấy chi tiết đơn hàng
        response = requests.get(order_service_url, timeout=5)
        response.raise_for_status()  # Ném lỗi nếu không phải 200 OK
        order_data = response.json()
        
        # Lấy thông tin cần thiết từ JSON
        total_amount = order_data.get("total_amount")
        items = order_data.get("items", [])
        
        # Sử dụng transaction để đảm bảo tính toàn vẹn dữ liệu
        with transaction.atomic():
            # Tạo bản ghi Payment
            payment = Payment.objects.create(
                order_id=order_id,
                amount=total_amount,
                status="paid",  # Thanh toán thành công
                method="paypal"  # Phương thức là PayPal
            )
            
            # Tạo các PaymentItem từ danh sách items
            for item in items:
                PaymentItem.objects.create(
                    payment=payment,
                    product_id=item["product_id"],
                    product_name=item["product_details"]["name"],
                    service_name=item["service_name"],
                    quantity=item["quantity"],
                    price=item["price"]
                )
        
        return True, "Payment and items created successfully"
    
    except requests.exceptions.RequestException as e:
        return False, f"Failed to fetch order details: {str(e)}"
    except Exception as e:
        return False, f"Error creating payment: {str(e)}"

def update_order_payment_status(order_id):
    # URL API của order_service để cập nhật
    order_service_url = f"http://127.0.0.1:7001/api/orders/{order_id}/"
    
    # Payload để cập nhật payment_status
    payload = {
        "payment_status": "paid"
    }
    
    try:
        # Gọi API PATCH để cập nhật trạng thái
        response = requests.patch(order_service_url, json=payload, timeout=5)
        response.raise_for_status()  # Ném lỗi nếu không phải 200 OK
        
        return True, "Order payment status updated to 'paid'"
    
    except requests.exceptions.RequestException as e:
        return False, f"Failed to update order status: {str(e)}"
    
