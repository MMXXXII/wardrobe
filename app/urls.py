# app/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from wardrobe.api import (
    CategoryViewSet,
    ProductViewSet,
    CustomerViewSet,
    StoreViewSet,
    OrderViewSet,
    UserProfileViewSet
)
from wardrobe import views

# создаём роутер DRF
router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("customers", CustomerViewSet, basename="customer")
router.register("stores", StoreViewSet, basename="store")
router.register("orders", OrderViewSet, basename="order")
router.register("userprofiles", UserProfileViewSet, basename="userprofile")

urlpatterns = [
    path('', views.ShowStoreView.as_view(), name="home"),  # главная страница магазина
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),  # для DRF login/logout
]

# добавляем статические файлы и медиа в DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
