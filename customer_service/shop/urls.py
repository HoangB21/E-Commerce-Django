from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('mobiles/', views.mobile_list, name='mobile_list'),
    path('detail/<int:mobile_id>/', views.mobile_detail, name='mobile_detail'),
    path('books/', views.book_list, name='book_list'),
    path('book/detail/<int:book_id>/', views.book_detail, name='book_detail'),
]