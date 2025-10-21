from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.conf import settings

from wardrobe.api import BrandViewSet, CategoryViewSet, ItemViewSet, StoreViewSet, PurchaseViewSet

from wardrobe import views

router = DefaultRouter()
router.register('brands', BrandViewSet, basename="brand")
router.register('categories', CategoryViewSet, basename="category")
router.register('items', ItemViewSet, basename="item")
router.register('stores', StoreViewSet, basename="store")
router.register('purchases', PurchaseViewSet, basename="purchase")

urlpatterns = [
    path('', views.ShowItemView.as_view()),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)