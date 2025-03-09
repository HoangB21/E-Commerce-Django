from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['house_number', 'street', 'district', 'city', 'country']

class CustomerRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=15, required=True)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})  # Hiển thị input dạng date picker
    )
    
    class Meta:
        model = Customer
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'password1', 'password2']
    
    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.phone = self.cleaned_data['phone']
        customer.date_of_birth = self.cleaned_data['date_of_birth']

        if commit:
            customer.save()
        
        return customer
