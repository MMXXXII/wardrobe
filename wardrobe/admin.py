from django.contrib import admin
from .models import Category, Store, Product, Customer, Order, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user")
    list_filter = ("user",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "user")
    list_filter = ("user",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "store", "size", "price", "get_user")
    list_filter = ("category", "store")

    def get_user(self, obj):
        return obj.user.username if obj.user else "-"
    get_user.short_description = "Пользователь"



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "store", "user")
    list_filter = ("store", "user")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "product", "customer", "status", "quantity", "total_price", "user")
    list_filter = ("status", "product", "customer")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "age", "address")
