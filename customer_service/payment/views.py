from django.shortcuts import render
from django.http import JsonResponse
import requests
import logging

PAYMENT_SERVICE_URL='http://127.0.0.1:7002/api/payments/'

def checkout(request):
    """
    Hiển thị trang thanh toán với thông tin đơn hàng.
    """
    customer_id = request.user.id
    response = requests.post(
        "http://127.0.0.1:7001/api/orders/",
        json={"customer_id": customer_id}
    )
    print(response.json())
    if response.status_code == 201:
        order = response.json()
    else:
        return JsonResponse({"error": "Order not found"}, status=404)
    return render(request, "order_detail.html", {"order": order})

def initiate_payment(request, order_id):
    # Chuẩn bị dữ liệu gửi đi
    payload = {
        "order_id": order_id
    }
    
    # Gọi API tới payment_service
    payment_service_url = f"{PAYMENT_SERVICE_URL}initiate-payment/"
    try:
        response = requests.post(payment_service_url, json=payload, timeout=5)
        response.raise_for_status()  # Ném lỗi nếu không phải 200 OK
        data = response.json()
        
        # Lấy paypal_form từ phản hồi
        paypal_form_html = data.get("paypal_form")
        if not paypal_form_html:
            return render(request, 'error.html', {"message": "Failed to initiate payment"})
        
        # Trả về giao diện chứa form PayPal
        return render(request, 'payment.html', {"paypal_form_html": paypal_form_html})
    
    except requests.exceptions.RequestException as e:
        # Xử lý lỗi khi gọi API thất bại
        return render(request, 'error.html', {"message": f"Payment service error: {str(e)}"})


logger = logging.getLogger(__name__)

def payment_detail(request, order_id):
    payment_service_url = f"{PAYMENT_SERVICE_URL}detail/{order_id}/"
    try:
        response = requests.get(payment_service_url, timeout=5)
        response.raise_for_status()
        payment_data = response.json()
        # Tính tổng cho từng item
        for item in payment_data['items']:
            item['total'] = float(item['price']) * float(item['quantity'])
        logger.info("Payment details fetched for order_id %s", order_id)
        return render(request, 'payment_detail.html', {'payment': payment_data})
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch payment details for order_id %s: %s", order_id, str(e))
        return render(request, 'error.html', {'message': f"Failed to fetch payment details: {str(e)}"})

def payment_success(request):
    # Xử lý khi thanh toán thành công
    order_id = request.GET.get('invoice')  # Lấy order_id từ query string của PayPal
    return render(request, 'success.html', {"order_id": order_id})

def payment_cancel(request):
    # Xử lý khi khách hàng hủy thanh toán
    order_id = request.GET.get('invoice')
    return render(request, 'cancel.html', {"order_id": order_id})