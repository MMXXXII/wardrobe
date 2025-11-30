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
class CustomerSerializer(serializers.ModelSerializer):
    """
    Сериализатор для User (покупателя).
    Показывает User с информацией о статусе и профиле.
    """
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'age'
        ]
        read_only_fields = ['id', 'is_staff']
    
    def get_age(self, obj):
        """Получаем возраст из профиля пользователя"""
        try:
            profile = UserProfile.objects.get(user=obj)
            return profile.age
        except UserProfile.DoesNotExist:
            return None
    
    def create(self, validated_data):
        """Создаём User и профиль"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password', ''),
            is_superuser=validated_data.get('is_superuser', False),
            is_staff=validated_data.get('is_superuser', False)
        )
        
        # Создаём профиль с возрастом если указан
        age = self.context.get('request').data.get('age')
        if age:
            UserProfile.objects.create(user=user, age=age)
        else:
            UserProfile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        """Обновляем User и профиль"""
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        instance.is_staff = validated_data.get('is_superuser', instance.is_superuser)
        instance.save()
        
        # Обновляем профиль
        age = self.context.get('request').data.get('age')
        if age is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.age = age
            profile.save()
        
        return instance

# -----------------------------
# Сериализаторы для заказов
# -----------------------------
class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=False,   # делаем необязательным
        allow_null=True
    )
    order_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'product', 'quantity', 'total']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        # Если customer не передан, создаём автоматически для текущего юзера
        if not validated_data.get('customer') and user:
            product = validated_data.get('product')
            customer, _ = Customer.objects.get_or_create(
                user=user,
                defaults={'first_name': user.first_name or user.username,
                          'last_name': user.last_name or '',
                          # можно добавить другие обязательные поля, например:
                          # 'store': product.store
                         }
            )
            validated_data['customer'] = customer
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # При обновлении проверяем, что product имеет store
        product = validated_data.get('product', instance.product)
        if product and not product.store:
            raise serializers.ValidationError("Product must have a store")
        
        return super().update(instance, validated_data)



# -----------------------------
# Сериализатор для профиля пользователя
# -----------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'age', 'address']
