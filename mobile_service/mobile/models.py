from django.db import models

class MobileDevice(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Tên model
    brand = models.CharField(max_length=50)                     # Hãng sản xuất
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá bán
    stock = models.PositiveIntegerField(default=0)              # Số lượng trong kho
    image = models.URLField(max_length=200, blank=True, null=True)  # URL hình ảnh
    service = models.CharField( max_length=20, default='mobile')  # Service chứa sản phẩm
    created_at = models.DateTimeField(auto_now_add=True)        # Thời gian thêm
    updated_at = models.DateTimeField(auto_now=True)            # Thời gian cập nhật
    screen_size = models.CharField(max_length=20, blank=True, null=True)  # Kích thước màn hình
    ram = models.CharField(max_length=10, blank=True, null=True)          # RAM
    storage = models.CharField(max_length=10, blank=True, null=True)      # Dung lượng lưu trữ
    camera = models.CharField(max_length=50, blank=True, null=True)       # Camera

    def __str__(self):
        return f"{self.brand} {self.name} ({self.service})"

    class Meta:
        verbose_name = "Mobile Device"
        verbose_name_plural = "Mobile Devices"