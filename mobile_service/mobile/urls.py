from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MobileDeviceViewSet

router = DefaultRouter()
router.register(r'api/mobiles', MobileDeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]