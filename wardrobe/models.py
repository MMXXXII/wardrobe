from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import pyotp


class Category(models.Model):
    name = models.TextField("Категория")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Store(models.Model):
    name = models.TextField("Название магазина")
    address = models.TextField("Адрес")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
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
    quantity = models.PositiveIntegerField("Количество", default=0)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return f"{self.name} ({self.size})"
    
    def is_available(self):
        return self.quantity > 0


class Customer(models.Model):
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
    order_id = models.AutoField(primary_key=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self) -> str:
        return f"{self.product} → {self.customer} ({self.status})"
    
    def save(self, *args, **kwargs):
        if self._state.adding and not self.order_id:
            last_order = Order.objects.order_by('-order_id').first()
            self.order_id = (last_order.order_id + 1) if last_order else 1
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True, verbose_name='Возраст')
    address = models.TextField("Адрес доставки", null=True, blank=True)
    totp_key = models.CharField(max_length=128, null=True, blank=True, default=pyotp.random_hex)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль {self.user.username}'

    def save(self, *args, **kwargs):
        if self.id is None and not self.totp_key:
            self.totp_key = pyotp.random_base32()
        super().save(*args, **kwargs)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)