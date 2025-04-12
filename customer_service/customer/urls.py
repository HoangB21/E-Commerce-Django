from django.urls import include, path
from .views import register, home, user_login, CustomerViewSet
from rest_framework.routers import DefaultRouter

# Tạo router cho ViewSet
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('', home, name='home'),
    path('api/', include(router.urls)),
]
