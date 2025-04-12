from djongo import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image_url = models.URLField(max_length=500)  # Lưu ảnh bằng URL
    service = models.CharField(max_length=100, default='books')  # Đặt giá trị mặc định là 'books'
    description = models.TextField()  # Mô tả sản phẩm
    author = models.CharField(max_length=100)
    publication_date = models.DateField()  # Ngày xuất bản
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')

    def __str__(self):
        return f"{self.name} by {self.author}"
