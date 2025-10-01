from django.db import models

class Brand(models.Model):
    name = models.TextField("Название бренда")
    description = models.TextField("Описание")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.TextField("Название категории")

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.TextField("Название вещи")
    color = models.TextField("Цвет")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.color})"


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
