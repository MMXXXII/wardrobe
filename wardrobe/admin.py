from django.contrib import admin
from .models import Brand, ClothingType, Buyer, Store, Purchase


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")


@admin.register(ClothingType)
class ClothingTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone")


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "brand", "clothing_type", "store", "amount", "date")
