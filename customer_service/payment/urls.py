from django.urls import path
from .views import checkout, initiate_payment, payment_cancel, payment_detail, payment_success

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path('initiate/<str:order_id>/', initiate_payment, name='initiate_payment'),
    path('success/', payment_success, name='payment-success'),
    path('cancel/', payment_cancel, name='payment-cancel'),
    path('detail/<int:order_id>/', payment_detail, name='payment_detail')
]
# 