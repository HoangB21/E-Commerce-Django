# filepath: /Users/hoangtong/Work Space/Class Material/2024-2025/S2/SA&D/E-Commerce_project/book_service/book/models.py
from djongo import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/')
    service = models.CharField(max_length=100, default='book')  # Đặt giá trị mặc định là 'book'
    description = models.TextField()  # Mô tả sản phẩm

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(Product):
    author = models.CharField(max_length=100)
    publication_date = models.DateField()  # Ngày xuất bản
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return f"{self.name} by {self.author}"