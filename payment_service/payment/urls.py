from django.urls import path, include
from .views import InitiatePaymentView, PaymentDetailView

urlpatterns = [
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('paypal-ipn/', include('paypal.standard.ipn.urls')),
    path('detail/<int:order_id>/', PaymentDetailView.as_view(), name='payment_detail'),
]