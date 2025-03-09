from django.shortcuts import render
import requests

def order_list(request):
    customer_id = request.user.id  # Giả sử bạn có thông tin user trong request
    order_api_url = f'http://127.0.0.1:8000/orders/customer/{customer_id}/'
    response = requests.get(order_api_url)

    if response.status_code == 200:
        orders = response.json()
    else:
        orders = []

    return render(request, 'customer/order_list.html', {'orders': orders})