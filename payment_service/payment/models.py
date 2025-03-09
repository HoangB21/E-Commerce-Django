from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField(unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"), ("cancel", "Cancel")],
        default="pending"
    )
    method = models.CharField(
        max_length=20,
        choices=[("paypal", "PayPal"), ("cod", "cod")],
        default="cod"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.order_id} - {self.status}"

class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, related_name="items", on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    service_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Product {self.product_name} - x{self.quantity}"
