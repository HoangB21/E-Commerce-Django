import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Mapping service_name với URL của service tương ứng
SERVICE_API_MAP = {
    "books": "http://book_service:8000/api/books/",
    "mobiles": "http://mobile_service:8001/api/mobiles/",
}

COMMENT_API_URL = "http://comment_service:7004/api/comments/"

def comment_page(request, service_name, product_id):
    # Kiểm tra service_name hợp lệ
    if service_name not in SERVICE_API_MAP:
        return render(request, "comment.html", {
            "error": f"Service '{service_name}' not supported"
        })

    # Lấy thông tin sản phẩm từ service tương ứng
    product_api_url = SERVICE_API_MAP[service_name]
    product_response = requests.get(f"{product_api_url}{product_id}/")
    product = product_response.json() if product_response.status_code == 200 else {}

    # Lấy danh sách comment từ comment_service
    comment_response = requests.get(COMMENT_API_URL, params={"product_id": product_id, "service_name": service_name})
    comments = comment_response.json() if comment_response.status_code == 200 else []

    context = {
        "product": {
            "id": product.get("id", product_id),
            "name": product.get("name", "Unknown Product"),
            "image_url": product.get("image_url", ""),
            "price": product.get("price", 0.0),
        },
        "service_name": service_name,
        "comments": comments,
    }
    return render(request, "comment.html", context)

@login_required
def add_comment(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        service_name = request.POST.get("service_name")
        content = request.POST.get("content")

        payload = {
            "customer_id": request.user.id,
            "product_id": product_id,
            "service_name": service_name,
            "content": content,
        }
        headers = {
            "Content-Type": "application/json",
        }

        print("Payload:", payload)
        
        response = requests.post(COMMENT_API_URL, json=payload, headers=headers)
        
        if response.status_code == 201:
            messages.success(request, "Comment added successfully")
            return redirect("comment_page", service_name=service_name, product_id=product_id)
        else:
            messages.error(request, "Failed to add comment")
            return redirect("comment_page", service_name=service_name, product_id=product_id)
    
    # Nếu không phải POST, quay lại trang comment
    return redirect("comment_page", service_name=request.POST.get("service_name", ""), product_id=request.POST.get("product_id", ""))