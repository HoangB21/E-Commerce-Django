from django.db import models

class Shipment(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
    ]

    order_id = models.IntegerField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="waiting"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipment for Order #{self.order_id} - {self.status}"

class ShipmentStatusHistory(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="status_history", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=Shipment.STATUS_CHOICES
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True, null=True)  # Ghi chú tùy chọn

    def __str__(self):
        return f"{self.shipment.order_id} - {self.status} at {self.changed_at}"