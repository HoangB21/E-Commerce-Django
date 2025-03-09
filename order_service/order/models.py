from django.db import models

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )

    SHIPPING_STATUS = (
        ('waiting', 'Waiting'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    customer_id = models.IntegerField()  # ID khách hàng từ customer_service
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    shipping_status = models.CharField(max_length=20, choices=SHIPPING_STATUS, default='waiting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.status} - Payment: {self.payment_status} - Shipping: {self.shipping_status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=255)  # ID sản phẩm từ book_service
    service_name = models.CharField(max_length=50)  # Tên service (book, mobile, clothes)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product_id} in Order {self.order.id}"
