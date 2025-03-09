from django.http import JsonResponse
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

SERVICE_APIS = {
    "book": "http://127.0.0.1:8000/api/books/",
    "mobile": "http://127.0.0.1:8001/api/mobiles/",
    "clothes": "http://127.0.0.1:8002/api/clothes/",
}

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request):
        """Tạo giỏ hàng mới cho khách hàng"""
        customer_id = request.data.get("customer_id")

        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='customer/(?P<customer_id>[^/.]+)')
    def get_cart(self, request, customer_id=None):
        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = get_cart_details(customer_id)
        return Response(cart_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='customer/(?P<customer_id>[^/.]+)/clear')
    def clear_cart(self, request, customer_id):
        """Xóa toàn bộ giỏ hàng"""
        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer_id=customer_id)
        for item in cart.items.all():
            item.delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        customer_id = request.data.get("customer_id")
        product_id = request.data.get("product_id")
        service_name = request.data.get("service_name")
        quantity = request.data.get("quantity", 1)

        if not all([customer_id, product_id, service_name]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra giỏ hàng của khách hàng
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)

        # Kiểm tra sản phẩm đã tồn tại trong giỏ hàng chưa
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id, service_name=service_name,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='update-item')
    def update_item(self, request):
        customer_id = request.data.get("customer_id")
        product_id = request.data.get("product_id")
        service_name = request.data.get("service_name")
        quantity = request.data.get("quantity")

        if not all([customer_id, product_id, service_name, quantity]):
            print(request.data)
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer_id=customer_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, service_name=service_name)
        cart_item.quantity = quantity
        cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='remove-item')
    def remove_item(self, request):
        customer_id = request.data.get("customer_id")
        product_id = request.data.get("product_id")
        service_name = request.data.get("service_name")

        if not all([customer_id, product_id, service_name]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer_id=customer_id)
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id, service_name=service_name)
        cart_item.delete()

        return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

def fetch_product_details(service_name, product_id):
    """Gọi API đến service tương ứng để lấy thông tin sản phẩm"""
    base_url = SERVICE_APIS.get(service_name)
    if not base_url:
        return None  # Nếu không có service phù hợp, bỏ qua
    
    response = requests.get(f"{base_url}{product_id}/")
    product_data = response.json()
    if response.status_code == 200:
        if 'price' in product_data:
            product_data['price'] = float(product_data['price'])
        # print(product_data)  # In ra dữ liệu nhận về
        return product_data
    return None

def get_cart_details(customer_id):
    """Lấy thông tin giỏ hàng của một khách hàng"""
    cart = get_object_or_404(Cart, customer_id=customer_id)
    cart_items = CartItem.objects.filter(cart=cart)

    cart_data = {
        "customer_id": customer_id,
        "items": [],
        "total_price": 0.0
    }

    for item in cart_items:
        product_details = fetch_product_details(item.service_name, item.product_id)
        total_price = float(product_details['price']) * item.quantity if product_details else 0
        cart_data["items"].append({
            "product_id": item.product_id,
            "service_name": item.service_name,
            "quantity": item.quantity,
            "product_details": product_details,  # Thông tin chi tiết sản phẩm
            "total": total_price  # Tổng giá của sản phẩm
        })
        cart_data["total_price"] += float(total_price)  # Cộng dồn tổng giá của giỏ hàng
    print(cart_data)
    return cart_data