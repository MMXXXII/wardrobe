import io
from django.contrib.auth import authenticate, login, logout as django_logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count, Avg, Sum
from openpyxl import Workbook
from rest_framework import permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from wardrobe.models import Category, Store, Product, Order, Customer, UserProfile, User
from wardrobe.serializers import (
    CategorySerializer, StoreSerializer, ProductSerializer,
    CustomerSerializer, OrderSerializer
)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserProfileViewSet(GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @method_decorator(ensure_csrf_cookie)
    @action(detail=False, url_path="csrf", methods=["GET"])
    def csrf(self, request, *args, **kwargs):
        return Response({"ok": True})

    @action(detail=False, url_path="info", methods=["GET"])
    def info(self, request, *args, **kwargs):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username if user.is_authenticated else "",
            "is_authenticated": user.is_authenticated,
            "is_superuser": user.is_superuser if user.is_authenticated else False
        })

    @action(detail=False, url_path="login", methods=["POST"])
    def login_first_factor(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )
        login(request, user)
        UserProfile.objects.get_or_create(user=user)
        return Response({
            "success": True,
            "is_authenticated": True,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser
        })

    @action(detail=False, url_path="logout", methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request, *args, **kwargs):
        django_logout(request)
        return Response({"success": True})


class BaseExportMixin:
    def export_queryset(self, queryset, columns, filename_base):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = filename_base
        sheet.append(columns)
        for row in queryset:
            sheet.append([row.get(col, "") for col in columns])
        buffer = io.BytesIO()
        workbook.save(buffer)
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


class CategoryViewSet(ModelViewSet, BaseExportMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        top = Category.objects.annotate(c=Count('product')).order_by('-c').first()
        return Response({'count': self.get_queryset().count(), 'top': top.name if top else None})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        data = [{'ID': c.id, 'Name': c.name, 'User': c.user.username if c.user else ''} for c in self.get_queryset()]
        return self.export_queryset(data, ['ID', 'Name', 'User'], 'Categories')


class StoreViewSet(ModelViewSet, BaseExportMixin):
    queryset = Store.objects.all().order_by('name')
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        top = Store.objects.annotate(c=Count('product__order')).order_by('-c').first()
        return Response({'count': self.get_queryset().count(), 'top': top.name if top else None})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        data = [{'ID': s.id, 'Name': s.name, 'Address': s.address, 'User': s.user.username if s.user else ''} for s in self.get_queryset()]
        return self.export_queryset(data, ['ID', 'Name', 'Address', 'User'], 'Stores')


class ProductViewSet(ModelViewSet, BaseExportMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        total = self.get_queryset().count()
        avg_price = self.get_queryset().aggregate(avg_price=Avg('price'))['avg_price'] or 0
        most_ordered = Order.objects.values('product__id', 'product__name').annotate(order_count=Count('product')).order_by('-order_count').first()
        return Response({
            'count': total,
            'avg_price': round(avg_price, 2),
            'most_ordered': most_ordered
        })

    @action(detail=False, methods=['GET'])
    def export(self, request):
        data = [{
            'ID': p.id,
            'Name': p.name,
            'Category': p.category.name if p.category else '',
            'Store': p.store.name if p.store else '',
            'Size': p.size,
            'Price': p.price,
            'Color': p.color or '',
            'Available': 'Yes' if p.is_available() else 'No'
        } for p in self.get_queryset()]
        return self.export_queryset(data, ['ID', 'Name', 'Category', 'Store', 'Size', 'Price', 'Color', 'Available'], 'Products')


class OrderViewSet(ModelViewSet, BaseExportMixin):
    queryset = Order.objects.select_related('product', 'customer', 'user')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        total = self.get_queryset().count()
        total_sum = self.get_queryset().aggregate(total=Sum('total_price'))['total'] or 0
        top_customer = self.get_queryset().values('customer__first_name').annotate(order_count=Count('order_id')).order_by('-order_count').first()
        return Response({'count': total, 'total_sum': total_sum, 'topCustomer': top_customer})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        data = [{
            'ID': o.order_id,
            'Product': o.product.name if o.product else '',
            'Customer': f"{o.customer.first_name} {o.customer.last_name or ''}" if o.customer else '',
            'Quantity': o.quantity,
            'Total Price': o.total_price,
            'Status': o.get_status_display(),
            'Order Date': o.order_date,
            'Delivery Date': o.delivery_date or 'Not delivered',
            'User': o.user.username if o.user else ''
        } for o in self.get_queryset()]
        return self.export_queryset(data, ['ID', 'Product', 'Customer', 'Quantity', 'Total Price', 'Status', 'Order Date', 'Delivery Date', 'User'], 'Orders')


class CustomerViewSet(ModelViewSet, BaseExportMixin):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        qs = self.get_queryset()
        total_users = qs.count()
        total_admins = qs.filter(is_superuser=True).count()
        return Response({'count': total_users, 'count_admins': total_admins, 'count_users': total_users - total_admins})

    def create(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.create_user(username=data['username'], email=data['email'], password=data['password'], is_superuser=data.get('is_superuser', False))
        UserProfile.objects.get_or_create(user=user, defaults={'age': data.get('age', None)})
        return Response(self.get_serializer(user).data, status=201)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data
        if 'password' in data:
            user.set_password(data['password'])
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.is_superuser = data.get('is_superuser', user.is_superuser)
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if 'age' in data:
            profile.age = data['age']
            profile.save()
        return Response(self.get_serializer(user).data)

    @action(detail=False, methods=['GET'])
    def export(self, request):
        data = []
        for u in self.get_queryset():
            profile = getattr(u, 'userprofile', None)
            data.append({
                'ID': u.id,
                'Username': u.username,
                'Email': u.email,
                'Age': profile.age if profile else '',
                'Role': 'Администратор' if u.is_superuser else 'Покупатель'
            })
        return self.export_queryset(data, ['ID', 'Username', 'Email', 'Age', 'Role'], 'Customers')
