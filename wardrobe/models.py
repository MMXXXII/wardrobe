from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_key = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.user.username if self.user else 'Без пользователя'


class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    picture = models.ImageField("Логотип", null=True, blank=True, upload_to="brands")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="brands")

    def __str__(self):
        return self.name if self.name else 'Без названия'


class ClothingType(models.Model):
    name = models.CharField("Тип одежды", max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="clothing_types")

    def __str__(self):
        return self.name if self.name else 'Без названия'


class Buyer(models.Model):
    name = models.CharField("Имя покупателя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="buyers")

    def __str__(self):
        return self.name if self.name else 'Без имени'


class Store(models.Model):
    name = models.CharField("Название магазина", max_length=100)
    address = models.CharField("Адрес", max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="stores")

    def __str__(self):
        return self.name if self.name else 'Без названия'


class Purchase(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="purchases")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, related_name="purchases")
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.SET_NULL, null=True, related_name="purchases")
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField("Количество")
    date = models.DateField("Дата покупки")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="purchases")

    def __str__(self):
        buyer_name = self.buyer.name if self.buyer else 'Без покупателя'
        brand_name = self.brand.name if self.brand else 'Без бренда'
        clothing_name = self.clothing_type.name if self.clothing_type else 'Без типа'
        return f"{buyer_name} - {brand_name} ({clothing_name})"