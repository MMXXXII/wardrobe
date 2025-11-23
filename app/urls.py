# app/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from wardrobe.api import (
    BrandViewSet,
    ClothingTypeViewSet,
    BuyerViewSet,
    StoreViewSet,
    PurchaseViewSet,
)
from wardrobe.views import UserProfileViewSet
from wardrobe import views

# создаём роутер DRF
router = DefaultRouter()
router.register("brands", BrandViewSet, basename="brand")
router.register("clothing-types", ClothingTypeViewSet, basename="clothingtype")
router.register("buyers", BuyerViewSet, basename="buyer")
router.register("stores", StoreViewSet, basename="store")
router.register("purchases", PurchaseViewSet, basename="purchase")
router.register("userprofile", UserProfileViewSet, basename="userprofile")

urlpatterns = [
    path('', views.ShowStoreView.as_view()),  # главная страница магазина
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('rest_framework.urls')),  # для DRF login/logout
]

# добавляем статические файлы и медиа в DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
