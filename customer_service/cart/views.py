from django.shortcuts import render, redirect
from django.contrib import messages
import requests

import os
from dotenv import load_dotenv

load_dotenv()

# Kiểm tra nếu đang chạy trong Docker
def is_running_in_docker():
    return os.path.exists('/.dockerenv') or os.getenv('RUNNING_IN_DOCKER') == 'true'

if is_running_in_docker():
    CART_SERVICE_URL = os.getenv('CART_SERVICE_URL_DOCKER')
else:
    CART_SERVICE_URL = os.getenv('CART_SERVICE_URL_LOCAL')

def view_cart(request):
    """Hiển thị giỏ hàng bằng cách gọi API từ cart_service"""
    customer_id = request.user.id  # Lấy ID khách hàng đang đăng nhập

    try:
        # Gọi API từ cart_service để lấy toàn bộ thông tin giỏ hàng
        print("api", f"{CART_SERVICE_URL}customer/{customer_id}/")
        cart_response = requests.get(f"{CART_SERVICE_URL}customer/{customer_id}/")
        if cart_response.status_code != 200:
            messages.error(request, "Không thể lấy giỏ hàng.")
            return render(request, "cart_detail.html", {"cart": None})

        cart_data = cart_response.json()

    except requests.RequestException:
        messages.error(request, "Lỗi kết nối đến dịch vụ giỏ hàng.")
        cart_data = None
    return render(request, "cart_detail.html", {
        "cart": cart_data,  # Truyền dữ liệu giỏ hàng từ cart_service sang template
    })


def add_to_cart(request):
    """Thêm sản phẩm vào giỏ hàng của khách hàng"""
    if request.method == 'POST':
        customer_id = request.user.id
        product_id = request.POST.get('product_id')
        service_name = request.POST.get('service_name')
        quantity = request.POST.get('quantity', 1)
        print(f"Adding product to cart: {product_id}, {service_name}, {quantity}")
        if not all([product_id, service_name]):
            messages.error(request, "Missing required fields.")
            return redirect('home')

        try:
            # Gửi yêu cầu POST đến cart_service để thêm sản phẩm vào giỏ hàng
            response = requests.post(f"{CART_SERVICE_URL}add-item/", data={
                'customer_id': customer_id,
                'product_id': product_id,
                'service_name': service_name,
                'quantity': quantity
            })

            if response.status_code == 201:
                messages.success(request, "Product added to cart successfully!")
            else:
                messages.error(request, "Failed to add product to cart.")

        except requests.RequestException as e:
            messages.error(request, "Error connecting to cart service.")
            print(f"Error adding product to cart: {e}")

    # Redirect về trang giỏ hàng hoặc trang khác tùy theo yêu cầu của bạn
    return redirect('view_cart')

def update_cart_item(request, product_id):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    if request.method == 'POST':
        customer_id = request.user.id
        quantity = request.POST.get('quantity', 1)
        service_name = request.POST.get('service_name')

        try:
            # Gửi yêu cầu POST đến cart_service để cập nhật số lượng sản phẩm trong giỏ hàng
            response = requests.post(f"{CART_SERVICE_URL}update-item/", data={
                'customer_id': customer_id,
                'product_id': product_id,
                'quantity': quantity,
                'service_name': service_name
            })

            if response.status_code == 200:
                messages.success(request, "Cart item updated successfully!")
            else:
                messages.error(request, "Failed to update cart item.")

        except requests.RequestException as e:
            messages.error(request, "Error connecting to cart service.")
            print(f"Error updating cart item: {e}")

    return redirect('view_cart')


def remove_cart_item(request, product_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    if request.method == 'POST':
        customer_id = request.user.id
        service_name = request.POST.get('service_name')
        try:
            # Gửi yêu cầu POST đến cart_service để xóa sản phẩm khỏi giỏ hàng
            response = requests.post(f"{CART_SERVICE_URL}remove-item/", data={
                'customer_id': customer_id,
                'product_id': product_id,
                'service_name': service_name
            })

            if response.status_code == 200:
                messages.success(request, "Cart item removed successfully!")
            else:
                messages.error(request, "Failed to remove cart item.")

        except requests.RequestException as e:
            messages.error(request, "Error connecting to cart service.")
            print(f"Error removing cart item: {e}")

    return redirect('view_cart')

