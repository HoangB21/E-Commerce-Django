from django.contrib.auth.models import AbstractUser
from django.db import models

class Address(models.Model):
    house_number = models.CharField(max_length=20)  # Số nhà
    street = models.CharField(max_length=255)  # Đường
    district = models.CharField(max_length=100)  # Quận/Huyện
    city = models.CharField(max_length=100)  # Tỉnh/Thành phố
    country = models.CharField(max_length=100, default="Vietnam")  # Quốc gia

    def __str__(self):
        return f"{self.house_number} {self.street}, {self.district}, {self.city}, {self.country}"

class Customer(AbstractUser):
    # Định nghĩa các loại khách hàng
    CUSTOMER_TYPES = (
        ('GUEST', 'Guest'),
        ('ONE_TIME', 'One-time'),
        ('REGULAR', 'Regular'),
        ('LOYAL', 'Loyal'),
        ('VIP', 'VIP'),
    )

    # Mối quan hệ One-to-One với Address
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Thông tin bổ sung
    phone = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Thêm trường customer_type
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='GUEST',  # Mặc định là khách hàng mua 1 lần
    )

    # Định nghĩa lại các trường quan hệ để tránh xung đột với AbstractUser
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customer_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customer_users_permissions",
        blank=True
    )

    # Các trường mặc định của AbstractUser
    email = models.EmailField(unique=True)  
    username = models.CharField(max_length=150, unique=True)  

    REQUIRED_FIELDS = ['address', 'phone', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"