from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from wardrobe.api import BrandViewSet, CategoryViewSet, ItemViewSet, StoreViewSet, PurchaseViewSet

router = DefaultRouter()
router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'items', ItemViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'purchases', PurchaseViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
