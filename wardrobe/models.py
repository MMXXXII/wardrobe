from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    picture = models.ImageField("Логотип", null=True, blank=True, upload_to="brands")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    picture = models.ImageField("Фото вещи", null=True, blank=True, upload_to="items")

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField("Название магазина", max_length=100)
    address = models.CharField("Адрес", max_length=200) 

    def __str__(self):
        return self.name


class Purchase(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField("Количество")
    date = models.DateField("Дата покупки")

    def __str__(self):
        return f"{self.item.name} - {self.store.name}"
