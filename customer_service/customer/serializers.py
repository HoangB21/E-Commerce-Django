from rest_framework import serializers
from .models import Address, Customer

# Serializer cho Address
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'house_number', 'street', 'district', 'city', 'country']
        read_only_fields = ['id']

# Serializer cho Customer
class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer()  # Nested serializer cho Address
    customer_type = serializers.ChoiceField(choices=Customer.CUSTOMER_TYPES, default='GUEST')

    class Meta:
        model = Customer
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'date_of_birth', 'customer_type', 'address', 'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        # Lấy dữ liệu address từ validated_data
        address_data = validated_data.pop('address', None)
        if address_data:
            address = Address.objects.create(**address_data)
            validated_data['address'] = address

        # Tạo user với password
        password = validated_data.pop('password', None)
        customer = Customer(**validated_data)
        if password:
            customer.set_password(password)  # Mã hóa password
        customer.save()
        return customer

    def update(self, instance, validated_data):
        # Cập nhật address nếu có
        address_data = validated_data.pop('address', None)
        if address_data:
            if instance.address:
                # Cập nhật address hiện tại
                for attr, value in address_data.items():
                    setattr(instance.address, attr, value)
                instance.address.save()
            else:
                # Tạo address mới
                instance.address = Address.objects.create(**address_data)

        # Cập nhật password nếu có
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Cập nhật các trường còn lại
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate_phone(self, value):
        if Customer.objects.filter(phone=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value