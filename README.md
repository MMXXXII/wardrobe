# Wardrobe

Приложение для управления одеждой, магазинами, заказами и пользователями.

## Описание

Проект позволяет:
- Управлять категориями одежды
- Добавлять товары в магазины
- Отслеживать заказы и покупателей
- Работать с профилями пользователей

## Установка

1. Клонируем репозиторий:
git clone https://github.com/ваш_пользователь/wardrobe.git
cd wardrobe

Создаем и активируем виртуальное окружение
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate


Устанавливаем зависимости:
pip install -r requirements.txt

Применяем миграции:
python manage.py migrate


Запускаем сервер:
python manage.py runserver

