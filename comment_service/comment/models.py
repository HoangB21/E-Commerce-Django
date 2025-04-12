from django.db import models

class Comment(models.Model):
    customer_id = models.IntegerField()  # Links to a customer from User Service
    product_id = models.CharField(max_length=255)  # Product identifier from Product Service
    service_name = models.CharField(max_length=50)  # Specifies product type (e.g., "book", "mobile")
    content = models.TextField()  # The text of the comment or review
    sentiment = models.CharField(max_length=20, choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')], null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on modification

    def __str__(self):
        return f"Comment on {self.product_id} ({self.service_name}) by Customer {self.customer_id}"