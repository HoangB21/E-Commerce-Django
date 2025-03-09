from rest_framework import viewsets, status
from rest_framework.response import Response
import requests
from rest_framework.decorators import action
from .models import Order, OrderItem
from .serializers import OrderSerializer

CART_SERVICE_URL = 'http://127.0.0.1:7000/api/carts/'  # Địa chỉ service cart

SERVICE_APIS = {
    "book": "http://127.0.0.1:8000/api/books/",
    "clothes": "http://127.0.0.1:8002/api/clothes/",
    "mobile": "http://127.0.0.1:8001/api/mobiles/",
}

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['get'], url_path='customer/(?P<customer_id>[^/.]+)')
    def list_orders_by_customer(self, request, customer_id=None):
        orders = Order.objects.filter(customer_id=customer_id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='customer/(?P<customer_id>\d+)/create-from-cart')
    def create_order_from_cart(self, request, customer_id=None):

        if not customer_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Gọi API của cart_service để lấy giỏ hàng của user
        cart_api_url = f'{CART_SERVICE_URL}customer/{customer_id}'  # Sử dụng tên service thay vì localhost
        cart_response = requests.get(cart_api_url)

        if cart_response.status_code != 200:
            return Response({'error': 'Could not retrieve cart information'}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = cart_response.json()

        # Kiểm tra nếu giỏ hàng trống
        if not cart_data['items']:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        print(cart_data['items'])

        # Thêm giá sản phẩm vào dữ liệu giỏ hàng
        for item in cart_data['items']:
            item['price'] = item['product_details']['price']

        # Tạo order từ dữ liệu giỏ hàng
        order_data = {
            'customer_id': customer_id,
            'total_amount': cart_data['total_price'],
            'status': 'pending',
            'payment_status': 'unpaid',
            'shipping_status': 'waiting',
            'items': cart_data['items']
        }

        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()
            
            # Gọi API xóa giỏ hàng sau khi tạo đơn hàng thành công
            requests.post(f'{CART_SERVICE_URL}customer/{customer_id}/clear/')

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='detail/(?P<order_id>\d+)')
    def get_detail_order(self, request, order_id=None):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        order_data = OrderSerializer(order).data

        for item in order_data['items']:
            product_id = item['product_id']
            service_name = item['service_name']
            item_detail_url = f'{SERVICE_APIS[service_name]}{product_id}/'
            item_response = requests.get(item_detail_url)

            if item_response.status_code == 200:
                item['product_details'] = item_response.json()
            else:
                item['product_details'] = {'error': 'Could not retrieve product details'}

            # Tính thành tiền
            item['total_price'] = float(item['price']) * item['quantity']

        return Response(order_data)


