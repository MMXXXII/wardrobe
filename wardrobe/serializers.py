from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Store, Product, Customer, Order, UserProfile

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
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'age'
        ]
        read_only_fields = ['id', 'is_staff']
    
    def get_age(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return profile.age
        except UserProfile.DoesNotExist:
            return None
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data.get('password', ''),
            is_superuser=validated_data.get('is_superuser', False),
            is_staff=validated_data.get('is_superuser', False)
        )
        
        age = self.context.get('request').data.get('age')
        if age:
            UserProfile.objects.create(user=user, age=age)
        else:
            UserProfile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)
        instance.is_staff = validated_data.get('is_superuser', instance.is_superuser)
        instance.save()
        
        age = self.context.get('request').data.get('age')
        if age is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.age = age
            profile.save()
        
        return instance


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        required=False,
        allow_null=True
    )
    order_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    customer_name = serializers.CharField(source='customer.first_name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    store = serializers.PrimaryKeyRelatedField(source='product.store', read_only=True)
    store_name = serializers.CharField(source='product.store.name', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_id', 'product', 'product_name',
            'customer', 'customer_name',
            'store', 'store_name',
            'quantity', 'order_date', 'status', 'total_price'
        ]
        read_only_fields = ['id', 'total_price']

    def _calculate_total(self, product, quantity):
        return product.price * quantity if product else 0

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        product = validated_data.get('product')
        quantity = validated_data.get('quantity', 1)

        if product.quantity < quantity:
            raise serializers.ValidationError(
                f"Недостаточно товара на складе. Доступно: {product.quantity}"
            )

        if user:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            customer, _ = Customer.objects.get_or_create(
                user=user,
                store=product.store,
                defaults={
                    'first_name': user.first_name or user.username,
                    'last_name': user.last_name or '',
                    'email': user.email or '',
                    'phone': getattr(profile, 'phone', None)
                }
            )
            validated_data['customer'] = customer

        validated_data['total_price'] = self._calculate_total(product, quantity)

        order = super().create(validated_data)

        if order.status in ['sold', 'pending']:
            product.quantity -= quantity
            product.save()

        return order

    def update(self, instance, validated_data):
        product = validated_data.get('product', instance.product)
        old_status = instance.status
        old_quantity = instance.quantity
        old_product = instance.product

        new_status = validated_data.get('status', old_status)
        new_quantity = validated_data.get('quantity', old_quantity)

        if old_status in ['sold', 'pending']:
            old_product.quantity += old_quantity
            old_product.save()

        if new_status in ['sold', 'pending']:
            if product.quantity < new_quantity:
                raise serializers.ValidationError(
                    f"Недостаточно товара на складе. Доступно: {product.quantity}"
                )
            product.quantity -= new_quantity
            product.save()

        instance.product = product
        instance.customer = validated_data.get('customer', instance.customer)
        instance.quantity = new_quantity
        instance.status = new_status
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.total_price = self._calculate_total(product, new_quantity)
        instance.save()

        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'age', 'address']
