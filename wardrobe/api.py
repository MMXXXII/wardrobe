import pyotp
from django.contrib.auth import authenticate, login, logout as django_logout
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count, Avg, Sum
import io
from openpyxl import Workbook
from docx import Document
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from wardrobe.models import Category, Store, Product, Order, Customer, UserProfile, User
from wardrobe.serializers import (
    CategorySerializer, StoreSerializer, ProductSerializer,
    CustomerSerializer, OrderSerializer
)
from wardrobe.permissions import IsSuperuserOrReadOnly


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class SecondLoginSerializer(serializers.Serializer):
    key = serializers.CharField()


class UserProfileViewSet(GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @method_decorator(ensure_csrf_cookie)
    @action(detail=False, url_path="csrf", methods=["GET"])
    def csrf(self, request, *args, **kwargs):
        return Response({"ok": True})

    def get_serializer_class(self):
        if self.action == "login_second_factor":
            return SecondLoginSerializer
        return LoginSerializer

    @action(detail=False, url_path="info", methods=["GET"])
    def info(self, request, *args, **kwargs):
        data = {
            "username": request.user.username if request.user.is_authenticated else "",
            "is_authenticated": request.user.is_authenticated,
            "is_superuser": request.user.is_superuser if request.user.is_authenticated else False,
            "second_factor": request.session.get("second_factor") or False
        }
        return Response(data)

    @action(detail=False, url_path="login", methods=["POST"])
    def login_first_factor(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )
        if user is None:
            return Response({"success": False, "error": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)
        
        login(request, user)
        request.session["second_factor"] = False
        request.session.modified = True
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        if not profile.totp_key:
            profile.totp_key = pyotp.random_base32()
            profile.save()
        
        return Response({
            "success": True,
            "is_authenticated": True,
            "first_factor": True,
            "second_factor": False,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser
        })

    @action(detail=False, url_path="otp-login", methods=["POST"], serializer_class=SecondLoginSerializer)
    def login_second_factor(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["key"].strip()
        profile = UserProfile.objects.filter(user=request.user).first()
        
        if not profile or not profile.totp_key:
            return Response({"success": False, "error": "Профиль не найден"})
        
        totp = pyotp.TOTP(profile.totp_key)
        if totp.verify(code, valid_window=1):
            request.session["second_factor"] = True
            request.session.set_expiry(600)
            return Response({
                "success": True,
                "is_authenticated": True,
                "second_factor": True,
                "is_superuser": request.user.is_superuser
            })
        
        return Response({"success": False, "error": "Неверный OTP код"})

    @action(detail=False, url_path="totp-url", methods=["GET"], permission_classes=[IsAuthenticated])
    def totp_url(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if not profile.totp_key:
            profile.totp_key = pyotp.random_base32()
            profile.save()
        
        totp = pyotp.TOTP(profile.totp_key)
        otp_uri = totp.provisioning_uri(name=request.user.username, issuer_name="MyWardrobeApp")
        return Response({"url": otp_uri})

    @action(detail=False, url_path="logout", methods=["POST"], permission_classes=[IsAuthenticated])
    def logout(self, request, *args, **kwargs):
        django_logout(request)
        request.session["second_factor"] = False
        request.session.modified = True
        return Response({"success": True})


class OTPRequiredForDelete(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.session.get("second_factor", False)


class BaseExportMixin:
    def export_queryset(self, queryset, columns, filename_base):
        file_type = self.request.query_params.get('type', 'excel')
        
        if file_type == 'excel':
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = filename_base
            sheet.append(columns)
            
            for data_row in queryset:
                row_data = [data_row.get(col, '') for col in columns]
                sheet.append(row_data)
            
            excel_file = io.BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)
            file_response = HttpResponse(
                excel_file,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            file_response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return file_response
        
        elif file_type == 'word':
            document = Document()
            document.add_heading(filename_base, 0)
            
            for data_row in queryset:
                row_values = [str(data_row.get(col, '')) for col in columns]
                text_line = ' | '.join(row_values)
                document.add_paragraph(text_line)
            
            word_file = io.BytesIO()
            document.save(word_file)
            word_file.seek(0)
            file_response = HttpResponse(
                word_file,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            file_response['Content-Disposition'] = f'attachment; filename="{filename_base}.docx"'
            return file_response
        
        return Response({"error": "Unknown file type"}, status=400)


class CategoryViewSet(ModelViewSet, BaseExportMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, OTPRequiredForDelete, IsSuperuserOrReadOnly]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        top_category = Category.objects.annotate(product_count=Count('product')).order_by('-product_count').first()
        top_name = top_category.name if top_category else None
        return Response({'count': total, 'top': top_name})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Только администраторы могут экспортировать данные"}, status=403)
        
        queryset = self.get_queryset()
        data_list = [{'ID': c.id, 'Name': c.name, 'User': c.user.username if c.user else ''} for c in queryset]
        columns = ['ID', 'Name', 'User']
        return self.export_queryset(data_list, columns, 'Categories')


class StoreViewSet(ModelViewSet, BaseExportMixin):
    queryset = Store.objects.all().order_by('name')
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, OTPRequiredForDelete, IsSuperuserOrReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Только админы могут добавлять магазины")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Только админы могут редактировать магазины")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionError("Только админы могут удалять магазины")
        instance.delete()

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        top_store = Store.objects.annotate(order_count=Count('product__order')).order_by('-order_count').first()
        top_name = top_store.name if top_store else None
        return Response({'count': total, 'top': top_name})

    @action(detail=False, methods=['GET'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Только администраторы могут экспортировать данные"}, status=403)
        
        queryset = self.get_queryset()
        data_list = [{'ID': s.id, 'Name': s.name, 'Address': s.address, 'User': s.user.username if s.user else ''} for s in queryset]
        columns = ['ID', 'Name', 'Address', 'User']
        return self.export_queryset(data_list, columns, 'Stores')


class ProductViewSet(ModelViewSet, BaseExportMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, OTPRequiredForDelete, IsSuperuserOrReadOnly]

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        avg_price = queryset.aggregate(avg_price=Avg('price'))['avg_price'] or 0
        most_ordered = Order.objects.values('product__id', 'product__name').annotate(order_count=Count('product')).order_by('-order_count').first()
        
        if most_ordered:
            most_ordered_product = {
                'id': most_ordered['product__id'],
                'name': most_ordered['product__name'],
                'order_count': most_ordered['order_count']
            }
        else:
            most_ordered_product = None
        
        return Response({
            'count': total,
            'avg_price': round(avg_price, 2),
            'most_ordered': most_ordered_product
        })

    @action(detail=False, methods=['GET'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Только администраторы могут экспортировать товары"}, status=403)
        
        queryset = self.get_queryset()
        data_list = [{
            'ID': p.id,
            'Name': p.name,
            'Category': p.category.name if p.category else '',
            'Store': p.store.name if p.store else '',
            'Size': p.size,
            'Price': p.price,
            'Color': p.color or '',
            'Available': 'Yes' if p.is_available() else 'No'
        } for p in queryset]
        
        columns = ['ID', 'Name', 'Category', 'Store', 'Size', 'Price', 'Color', 'Available']
        return self.export_queryset(data_list, columns, 'Products')


class OrderViewSet(ModelViewSet, BaseExportMixin):
    queryset = Order.objects.select_related('product', 'customer', 'user')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OTPRequiredForDelete]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            return queryset.filter(user=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == 'complete_order':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['POST'], url_path='complete')
    def complete_order(self, request, pk=None):
        order = self.get_object()
        
        if not request.user.is_superuser:
            return Response({'detail': 'Только администратор может менять статус заказа'}, status=403)
        
        if order.status == 'sold':
            return Response({'detail': 'Заказ уже завершен'}, status=400)
        
        from datetime import date
        order.status = 'sold'
        order.delivery_date = date.today()
        order.save()
        serializer = self.get_serializer(order)
        return Response({'detail': 'Заказ успешно завершен', 'order': serializer.data})

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = self.get_queryset()
        total = queryset.count()
        total_sum = queryset.aggregate(total=Sum('total_price'))['total'] or 0
        top_customer = queryset.values('customer__id', 'customer__first_name').annotate(order_count=Count('order_id')).order_by('-order_count').first()
        
        if top_customer:
            top_customer_data = {
                'name': top_customer['customer__first_name'],
                'order_count': top_customer['order_count']
            }
        else:
            top_customer_data = {'name': None, 'order_count': 0}
        
        return Response({
            'count': total,
            'total_sum': round(total_sum, 2),
            'topCustomer': top_customer_data
        })

    @action(detail=False, methods=['GET'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Только администраторы могут экспортировать данные"}, status=403)
        
        queryset = self.get_queryset()
        data_list = [{
            'ID': o.order_id,
            'Product': o.product.name if o.product else '',
            'Customer': f"{o.customer.first_name} {o.customer.last_name or ''}" if o.customer else '',
            'Quantity': o.quantity,
            'Total Price': o.total_price,
            'Status': o.get_status_display(),
            'Order Date': o.order_date,
            'Delivery Date': o.delivery_date or 'Not delivered',
            'User': o.user.username if o.user else ''
        } for o in queryset]
        
        columns = ['ID', 'Product', 'Customer', 'Quantity', 'Total Price', 'Status', 'Order Date', 'Delivery Date', 'User']
        return self.export_queryset(data_list, columns, 'Orders')


class CustomerViewSet(ModelViewSet, BaseExportMixin):
    queryset = User.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, OTPRequiredForDelete, IsSuperuserOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        queryset = self.get_queryset()
        total_users = queryset.count()
        total_admins = queryset.filter(is_superuser=True).count()
        return Response({
            'count': total_users,
            'count_admins': total_admins,
            'count_users': total_users - total_admins
        })

    def create(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        age = data.get('age', None)
        is_superuser = data.get('is_superuser', False)
        is_staff = data.get('is_staff', False)
        
        if not username or not email or not password:
            return Response({"error": "Заполните все обязательные поля"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким именем уже существует"}, status=400)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=is_superuser,
            is_staff=is_staff
        )
        
        UserProfile.objects.get_or_create(user=user, defaults={'age': age})
        
        store = Store.objects.first()
        if not store:
            store = Store.objects.create(name='Default Store', address='N/A', user=request.user)
        Customer.objects.get_or_create(user=user, defaults={'first_name': username, 'last_name': '', 'store': store})
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        data = request.data
        password = data.get('password', None)
        
        if password:
            user.set_password(password)
        
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.is_superuser = data.get('is_superuser', user.is_superuser)
        user.is_staff = data.get('is_staff', user.is_staff)
        user.save()
        
        age = data.get('age', None)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        if age is not None:
            profile.age = age
            profile.save()
        
        customer, _ = Customer.objects.get_or_create(user=user, defaults={'first_name': user.username, 'last_name': ''})
        customer.first_name = user.username
        customer.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Только администраторы могут экспортировать данные"}, status=403)
        
        queryset = self.get_queryset()
        data_list = []
        
        for u in queryset:
            age = ''
            if hasattr(u, 'userprofile'):
                age = u.userprofile.age if u.userprofile.age else ''
            
            data_list.append({
                'ID': u.id,
                'Username': u.username,
                'Email': u.email,
                'Age': age,
                'Role': 'Администратор' if u.is_superuser else 'Покупатель'
            })
        
        columns = ['ID', 'Username', 'Email', 'Age', 'Role']
        return self.export_queryset(data_list, columns, 'Customers')