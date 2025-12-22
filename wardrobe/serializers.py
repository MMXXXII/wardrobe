from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Store, Product, Customer, Order, UserProfile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'user']
        read_only_fields = ['user']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    store_name = serializers.StringRelatedField(source='store', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'store', 'store_name', 
                  'size', 'price', 'color', 'image', 'description', 'quantity']

class CustomerSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'age']
        read_only_fields = ['id']

    def get_age(self, obj):
        profile = UserProfile.objects.filter(user=obj).first()
        return profile.age if profile else None

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    store_name = serializers.CharField(source='product.store.name', read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'product', 'product_name', 'customer', 'customer_name',
                  'store_name', 'quantity', 'order_date', 'status', 'total_price']
        read_only_fields = ['order_id', 'total_price']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'age', 'address']
