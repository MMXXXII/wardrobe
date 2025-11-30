# app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from wardrobe.api import (
    CategoryViewSet,
    StoreViewSet,
    ProductViewSet,
    CustomerViewSet,
    OrderViewSet,
    UserProfileViewSet
)
from wardrobe import views

# Создаём роутер DRF
router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("stores", StoreViewSet, basename="store")
router.register("products", ProductViewSet, basename="product")
router.register("customers", CustomerViewSet, basename="customer")
router.register("orders", OrderViewSet, basename="order")
router.register("userprofile", UserProfileViewSet, basename="userprofile")

urlpatterns = [
    path('', views.ShowStoreView.as_view(), name="home"),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]

# Добавляем статические файлы и медиа в DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)