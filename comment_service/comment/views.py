from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.permissions import IsAuthenticated

# Import các thành phần cho sentiment analysis với TensorFlow
from transformers import TFAutoModelForSequenceClassification, AutoTokenizer
import numpy as np
import tensorflow as tf

# Đảm bảo dùng tf-keras
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"  # Dùng legacy Keras nếu cần

# Khởi tạo model và tokenizer global
MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)
labels = ['negative', 'neutral', 'positive']

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def get_sentiment(text):
    # Preprocess text
    processed_text = preprocess(text)
    
    # Tokenize
    encoded_input = tokenizer(processed_text, return_tensors='tf', truncation=True, max_length=512)
    
    # Predict với TensorFlow
    output = model(encoded_input)
    scores = output.logits[0].numpy()  # Lấy logits
    
    # Tính softmax với numpy
    exp_scores = np.exp(scores - np.max(scores))  # Trừ max để tránh overflow
    probabilities = exp_scores / np.sum(exp_scores)
    
    # Lấy sentiment
    sentiment_idx = np.argmax(probabilities)
    return labels[sentiment_idx]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Comment.objects.all()
        product_id = self.request.query_params.get('product_id')
        service_name = self.request.query_params.get('service_name')
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if service_name:
            queryset = queryset.filter(service_name=service_name)
        
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        try:
            # Lấy content từ request data
            content = self.request.data.get('content')
            if not content:
                raise ValueError("Content cannot be empty")

            print(f"Creating comment with content: {content}, customer_id: {self.request.data.get('customer_id')}")

            # Phân tích sentiment
            sentiment = get_sentiment(content)
            print(f"Sentiment analyzed: {sentiment}")

            # In dữ liệu serializer trước khi save để debug
            print(f"Serializer initial data: {serializer.initial_data}")

            # Lưu comment
            serializer.save(
                customer_id=self.request.data.get('customer_id'),
                sentiment=sentiment
            )
            print("Comment created successfully")

        except ValueError as ve:
            print(f"Validation error: {str(ve)}")
            raise

        except Exception as e:
            print(f"Error creating comment: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.customer_id != request.user.id:
            return Response(
                {"detail": "You can only delete your own comments"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)