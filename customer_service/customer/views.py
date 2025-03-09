# filepath: /Users/hoangtong/Work Space/Class Material/2024-2025/S2/SA&D/E-Commerce_project/customer_service/customer/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomerRegistrationForm, AddressForm
import requests

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        print("POST method detected")  # Kiểm tra phương thức POST
        user_form = CustomerRegistrationForm(request.POST)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            print("Forms are valid")  # Kiểm tra form hợp lệ
            try:
                address = address_form.save()
                user = user_form.save(commit=False)
                user.address = address
                user.save()
                
                print("User created:", user)  # Kiểm tra user vừa tạo
                login(request, user)
                messages.success(request, 'Account created successfully! Welcome!')
                return redirect('home')
            except Exception as e:
                print("Error during saving user:", e)  # In ra lỗi nếu không lưu được user
                messages.error(request, 'An error occurred. Please try again.')
        else:
            print("Form errors:", user_form.errors, address_form.errors)  # In ra lỗi nếu có
            messages.error(request, 'Invalid input. Please check your data.')
    
    else:
        print("GET method detected")  # Kiểm tra khi truy cập bằng GET
        user_form = CustomerRegistrationForm()
        address_form = AddressForm()

    return render(request, 'customer/register.html', {
        'user_form': user_form,
        'address_form': address_form
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Trying to authenticate user: {username}")  # Debug log

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful! Welcome back.')
            return redirect('home')  # Redirect về trang Home nếu thành công
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            print("Authentication failed")  # Debug log
    
    return render(request, 'customer/login.html')


def home(request):
    return render(request, 'customer/home.html')