from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """Категория одежды (аналог Genre)"""
    name = models.TextField("Категория")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Store(models.Model):
    """Магазин (аналог Library)"""
    name = models.TextField("Название магазина")
    address = models.TextField("Адрес")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Товар/Одежда (аналог Book)"""
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]
    
    name = models.TextField("Название товара")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Магазин")
    size = models.CharField("Размер", max_length=3, choices=SIZE_CHOICES, default='M')
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=0.00)
    color = models.CharField("Цвет", max_length=50, null=True, blank=True)
    image = models.ImageField("Фото товара", upload_to="products", null=True, blank=True)
    description = models.TextField("Описание", null=True, blank=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return f"{self.name} ({self.size})"
    
    def is_available(self):
        """Проверяет, доступен ли товар для покупки (не продан)"""
        return not Order.objects.filter(product=self, status='sold').exists()


class Customer(models.Model):
    """Покупатель (аналог Member)"""
    first_name = models.TextField("Имя")
    last_name = models.TextField("Фамилия", null=True, blank=True)
    phone = models.CharField("Телефон", max_length=20, null=True, blank=True)
    email = models.EmailField("Email", null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Магазин")
    photo = models.ImageField("Фото", upload_to="customers", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name or ''}".strip()


class Order(models.Model):
    """Заказ/Продажа (аналог Loan)"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('sold', 'Продано'),
        ('returned', 'Возвращено'),
        ('cancelled', 'Отменено'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="Покупатель")
    order_date = models.DateField("Дата заказа")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    quantity = models.PositiveIntegerField("Количество", default=1)
    total_price = models.DecimalField("Общая сумма", max_digits=10, decimal_places=2, default=0.00)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"{self.product} → {self.customer} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Автоматически рассчитываем общую стоимость"""
        if self.product:
            self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Расширение модели User для хранения дополнительной информации"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True, verbose_name='Возраст')
    address = models.TextField("Адрес доставки", null=True, blank=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль {self.user.username}'