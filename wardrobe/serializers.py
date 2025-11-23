from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Brand, ClothingType, Buyer, Store, Purchase

# -----------------------------
# Сериализаторы магазина одежды
# -----------------------------

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'picture', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class ClothingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingType
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = ['id', 'name', 'phone', 'user']
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


class PurchaseSerializer(serializers.ModelSerializer):
    buyer_name = serializers.StringRelatedField(source='buyer', read_only=True)
    brand_name = serializers.StringRelatedField(source='brand', read_only=True)
    clothing_type_name = serializers.StringRelatedField(source='clothing_type', read_only=True)
    store_name = serializers.StringRelatedField(source='store', read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'buyer', 'buyer_name',
            'brand', 'brand_name',
            'clothing_type', 'clothing_type_name',
            'store', 'store_name',
            'amount', 'date', 'user'
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


# -----------------------------
# Сериализаторы для 2FA/пользователя
# -----------------------------

class OTPSerializer(serializers.Serializer):
    key = serializers.CharField()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']
