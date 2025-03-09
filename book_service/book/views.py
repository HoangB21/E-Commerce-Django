from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Book, Category
from .serializers import BookSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        print("Received Data:", request.data)  # Debug dữ liệu request

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errors:", serializer.errors)  # Debug lỗi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs.get("pk"))
        
        # Debug: In dữ liệu request
        print("📥 Nhận request cập nhật sách:")
        print("🔹 Dữ liệu:", request.data)
        print("📂 File gửi lên:", request.FILES)

        # Chuyển request thành dict để có thể cập nhật
        updated_data = request.data.copy()

        # Nếu một trường không có trong request, giữ nguyên giá trị cũ
        for field in ["name", "author", "price", "stock", "category", "publication_date", "description", "image", "service"]:
            if field not in updated_data:
                updated_data[field] = getattr(book, field)

        # Debug: In dữ liệu sau khi xử lý
        print("🛠 Dữ liệu sau khi xử lý:", updated_data)

        # Validate và cập nhật dữ liệu
        serializer = self.get_serializer(book, data=updated_data, partial=True)
        
        if not serializer.is_valid():
            print("❌ Lỗi validation:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Cập nhật sách
        self.perform_update(serializer)

        print("✅ Cập nhật thành công, dữ liệu mới:", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs.get("pk"))

        # Debug: In thông tin sách cần xóa
        print(f"🗑 Xóa sách: {book.name} (ID: {book.id})")

        book.delete()
        return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)