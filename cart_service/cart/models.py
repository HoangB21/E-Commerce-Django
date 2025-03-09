from django.db import models
from django.db.models import JSONField

class Cart(models.Model):
    customer_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=255)  # ID sản phẩm
    service_name = models.CharField(max_length=50)  # Tên service (book, mobile, clothes)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product_id', 'service_name')  # Mỗi sản phẩm chỉ xuất hiện một lần trong giỏ hàng
