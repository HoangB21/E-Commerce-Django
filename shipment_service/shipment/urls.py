from django.urls import path
from .views import ShipmentCreateView, ShipmentDetailView, ShipmentUpdateView

urlpatterns = [
    path('create/', ShipmentCreateView.as_view(), name='shipment_create'),
    path('detail/<int:order_id>/', ShipmentDetailView.as_view(), name='shipment_detail'),
    path('update/<int:order_id>/', ShipmentUpdateView.as_view(), name='shipment_update'),
]