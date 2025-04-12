from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'customer_id', 'product_id', 'service_name', 'content', 
                 'sentiment', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Thêm validation nếu cần
        if not data.get('content').strip():
            raise serializers.ValidationError("Comment content cannot be empty")
        return data