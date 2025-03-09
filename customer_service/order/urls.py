from django.urls import path
from .views import cancel_order, proceed_to_checkout, shipment_detail, view_order_detail, view_orders

urlpatterns = [
    path('', view_orders, name='view_orders'),
    path('<int:order_id>/', view_order_detail, name='view_order_detail'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('checkout/', proceed_to_checkout, name='proceed_to_checkout'),
    path('shipment/detail/<int:order_id>/', shipment_detail, name='shipment_detail'),
]