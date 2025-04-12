from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^product/(?P<service_name>\w+)/(?P<product_id>[^/]+)/$', views.comment_page, name='comment_page'),
    path("add-comment/", views.add_comment, name="add_comment"),
]