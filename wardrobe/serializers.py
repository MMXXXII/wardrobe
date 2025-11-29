from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Store, Product, Customer, Order, UserProfile

# -----------------------------
# Сериализаторы для категории одежды
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------------
# Сериализаторы для магазинов
# -----------------------------
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------------
# Сериализаторы для товаров
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    store_name = serializers.StringRelatedField(source='store', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'store', 'store_name', 
                  'size', 'price', 'color', 'image', 'description']
        
# -----------------------------
# Сериализаторы для покупателей
# -----------------------------
class CustomerSerializer(serializers.ModelSerializer):
    store_name = serializers.StringRelatedField(source='store', read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'store', 'store_name', 'photo', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------------
# Сериализаторы для заказов
# -----------------------------
class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.StringRelatedField(source='product', read_only=True)
    customer_name = serializers.StringRelatedField(source='customer', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'product', 'product_name', 'customer', 'customer_name',
                  'order_date', 'delivery_date', 'status', 'quantity', 'total_price', 'user']
        read_only_fields = ['user', 'total_price']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------------
# Сериализатор для профиля пользователя
# -----------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'age', 'address']
