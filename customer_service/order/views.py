from django.shortcuts import render, redirect
from django.contrib import messages
import requests
import logging
from customer_service.utils import format_datetime


import os

# Kiểm tra nếu đang chạy trong Docker
def is_running_in_docker():
    return os.path.exists('/.dockerenv') or os.getenv('RUNNING_IN_DOCKER') == 'true'

# Tự động chọn URL phù hợp
if is_running_in_docker():
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL_DOCKER', 'http://order_service:7001/api/orders/')
    PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL_DOCKER', 'http://payment_service:7002/api/payments')
else:
    ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL_LOCAL', 'http://127.0.0.1:7001/api/orders/')
    PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL_LOCAL', 'http://127.0.0.1:7002/api/payments')

def view_orders(request):
    customer_id = request.user.id  # Giả sử bạn có thông tin user trong request
    order_api_url = f'{ORDER_SERVICE_URL}customer/{customer_id}/'
    response = requests.get(order_api_url)

    if response.status_code == 200:
        orders = response.json()
    else:
        orders = []
    for order in orders:
        if 'created_at' in order:
            order['created_at'] = format_datetime(order['created_at'])
    orders.sort(key=lambda x: x['created_at'], reverse=True)
    return render(request, 'order_list.html', {'orders': orders})

def view_order_detail(request, order_id):
    order_detail_api_url = f'{ORDER_SERVICE_URL}detail/{order_id}/'
    response = requests.get(order_detail_api_url)

    if response.status_code == 200:
        order_detail = response.json()
    else:
        order_detail = None
    print(order_detail)
    order_detail['created_at'] = format_datetime(order_detail['created_at'])

    return render(request, 'order_detail.html', {'order': order_detail}) 

def proceed_to_checkout(request):
    customer_id = request.user.id
    response = requests.post(f'{ORDER_SERVICE_URL}customer/{customer_id}/create-from-cart/')
    if response.status_code == 201:
        return redirect('view_orders')
    else:
        messages.error(request, 'Failed to proceed to checkout. Please try again.')
        return redirect('view_cart')


def cancel_order(request, order_id):
    if request.method == "POST":
        try:
            # Gọi API DELETE tới order_service
            order_service_url = f"{ORDER_SERVICE_URL}{order_id}/"
            response = requests.delete(order_service_url, timeout=5)
            if response.status_code == 204:  # 204 No Content là mã chuẩn khi xóa thành công
                logger.info("Order %s canceled successfully", order_id)
                messages.success(request, f"Order #{order_id} has been canceled successfully.")
            else:
                logger.error("Failed to cancel order %s: %s", order_id, response.text)
                messages.error(request, f"Failed to cancel Order #{order_id}. Please try again.")
        except requests.exceptions.RequestException as e:
            logger.error("Error canceling order %s: %s", order_id, str(e))
            messages.error(request, "An error occurred while canceling the order.")
        
        # Quay lại trang danh sách đơn hàng
        return redirect('view_orders')  # Giả sử 'order_list' là tên URL của danh sách
    
    return redirect('view_orders')  # Nếu không phải POST, quay lại danh sách

logger = logging.getLogger(__name__)

def shipment_detail(request, order_id):
    shipment_service_url = f"http://127.0.0.1:7003/api/shipments/detail/{order_id}/"
    try:
        response = requests.get(shipment_service_url, timeout=5)
        response.raise_for_status()
        shipment_data = response.json()
        # Format datetime fields
        if 'created_at' in shipment_data:
            shipment_data['created_at'] = format_datetime(shipment_data['created_at'])
        
        if 'status_history' in shipment_data:
            for status in shipment_data['status_history']:
                if 'changed_at' in status:
                    status['changed_at'] = format_datetime(status['changed_at'])

        print(shipment_data)
        logger.info("Shipment details fetched for order_id %s", order_id)
        return render(request, 'shipment_detail.html', {'shipment': shipment_data})
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch shipment details for order_id %s: %s", order_id, str(e))
        return render(request, 'error.html', {'message': f"Failed to fetch shipment details: {str(e)}"})