from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from wardrobe.models import Brand, Category, Item, Store, Purchase
import random

class Command(BaseCommand):
    help = 'Генерация случайных данных для моделей'

    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])

        # Создаем пользователей
        users = [User.objects.create_user(username=fake.user_name(), password='password123') for _ in range(10)]

        # Генерация Brands
        for _ in range(1000):
            user = random.choice(users)
            Brand.objects.create(
                name=fake.company(),
                description=fake.text(),
                user=user
            )

        # Генерация Categories
        for _ in range(1000):
            user = random.choice(users)
            Category.objects.create(
                name=fake.word(),
                user=user
            )

        # Генерация Items
        for _ in range(1000):
            user = random.choice(users)
            brand = random.choice(Brand.objects.all())
            category = random.choice(Category.objects.all())
            Item.objects.create(
                name=fake.word(),
                color=fake.color_name(),
                brand=brand,
                category=category,
                user=user
            )

        # Генерация Stores
        for _ in range(1000):
            user = random.choice(users)
            Store.objects.create(
                name=fake.company(),
                address=fake.address(),
                user=user
            )

        # Генерация Purchases
        for _ in range(1000):
            user = random.choice(users)
            item = random.choice(Item.objects.all())
            store = random.choice(Store.objects.all())
            amount = random.randint(1, 10)
            date = fake.date_this_decade()
            Purchase.objects.create(
                item=item,
                store=store,
                amount=amount,
                date=date,
                user=user
            )

        self.stdout.write(self.style.SUCCESS('Данные успешно сгенерированы!'))
