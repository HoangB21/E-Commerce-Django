from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_cart, name='view_cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:product_id>/', views.remove_cart_item, name='remove_cart_item'),
]