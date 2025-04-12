import requests
from django.shortcuts import render
import logging
from django.templatetags.static import static

logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv

load_dotenv()

# Kiểm tra nếu đang chạy trong Docker
def is_running_in_docker():
    return os.path.exists('/.dockerenv') or os.getenv('RUNNING_IN_DOCKER') == 'true'

# Tự động chọn URL phù hợp
if is_running_in_docker():
    MOBILE_SERVICE_URL = os.getenv('MOBILE_SERVICE_URL_DOCKER')
    BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL_DOCKER')
else:
    MOBILE_SERVICE_URL = os.getenv('MOBILE_SERVICE_URL_LOCAL')
    BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL_LOCAL')


def shop(request):
    categories = [
        {'name': 'Mobile', 'slug': 'mobiles', 'image': static('images/mobile_category.png'), 'description': 'Smartphones and accessories'},
        {'name': 'Book', 'slug': 'books', 'image': static('images/book_category.jpg'), 'description': 'Novels, textbooks, and more'},
        {'name': 'Clothes', 'slug': 'clothes', 'image': static('images/clothes_category.avif'), 'description': 'Fashion for all seasons'},
        {'name': 'Shoes', 'slug': 'shoes', 'image': static('images/shoes_category.avif'), 'description': 'Footwear for every style'},
    ]
    return render(request, 'shop.html', {'categories': categories})

def mobile_list(request):
    try:
        response = requests.get(f"{MOBILE_SERVICE_URL}", timeout=5)
        response.raise_for_status()
        mobiles = response.json()
        logger.info("Fetched mobile device list successfully")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch mobile devices: %s", str(e))
        mobiles = []
    return render(request, 'mobile_list.html', {'mobiles': mobiles})

def mobile_detail(request, mobile_id):
    try:
        response = requests.get(f"{MOBILE_SERVICE_URL}{mobile_id}/", timeout=5)
        response.raise_for_status()
        mobile = response.json()
        return render(request, 'mobile_detail.html', {'mobile': mobile})
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch mobile device %s: %s", mobile_id, str(e))
        return render(request, 'error.html', {'message': "Mobile device not found"})
    
def book_list(request):
    try:
        # Giả sử book_service chạy trên cổng 7005
        response = requests.get(BOOK_SERVICE_URL, timeout=5)
        response.raise_for_status()
        books = response.json()
        logger.info("Fetched book list successfully")
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch books: %s", str(e))
        books = []
    return render(request, 'book_list.html', {'books': books})

def book_detail(request, book_id):
    try:
        response = requests.get(f"{BOOK_SERVICE_URL}{book_id}/", timeout=5)
        response.raise_for_status()
        book = response.json()
        print(book)
        return render(request, 'book_detail.html', {'book': book})
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch book %s: %s", book_id, str(e))
        return render(request, 'error.html', {'message': "Book not found"})