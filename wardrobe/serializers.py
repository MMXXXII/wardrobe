from rest_framework import serializers
from .models import Brand, Category, Item, Store, Purchase

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "description"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ItemSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Item
        fields = ["id", "name", "color", "brand", "category"]

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "address"]

class PurchaseSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), source="item", write_only=True
    )
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source="store", write_only=True
    )

    class Meta:
        model = Purchase
        fields = ["id", "item", "store", "item_id", "store_id", "amount", "date"]
