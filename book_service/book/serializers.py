from rest_framework import serializers
from .models import Book, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'price', 'stock', 'image_url', 'category', 'category_name', 'publication_date', 'description', 'service']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None