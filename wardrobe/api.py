from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.core.cache import cache
import io
import time
import random
import string
from openpyxl import Workbook
import openpyxl
from docx import Document
from wardrobe.models import Customer
from django.contrib.auth.models import User
from openpyxl.styles import Font, PatternFill
from .models import Category, Store, Product, Order, UserProfile
from .serializers import (
    CategorySerializer, StoreSerializer, ProductSerializer,
    CustomerSerializer, OrderSerializer
)


class BaseExportMixin:
    def export_queryset(self, queryset, columns, filename_base):
        file_type = self.request.query_params.get('type', 'excel')

        if file_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.title = filename_base
            ws.append(columns)
            for row in queryset:
                ws.append([row.get(col, '') for col in columns])
            stream = io.BytesIO()
            wb.save(stream)
            stream.seek(0)
            response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.xlsx"'
            return response

        elif file_type == 'word':
            doc = Document()
            doc.add_heading(filename_base, 0)
            for row in queryset:
                doc.add_paragraph(' | '.join(str(row.get(col, '')) for col in columns))
            stream = io.BytesIO()
            doc.save(stream)
            stream.seek(0)
            response = HttpResponse(stream, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.docx"'
            return response

        return Response({"error": "Unknown file type"}, status=400)


class CategoryViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.all().order_by('name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        top_category = Category.objects.annotate(num_products=Count('product')).order_by('-num_products').first()
        return Response({
            'count': queryset.count(),
            'top': top_category.name if top_category else None
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        if request.user.is_superuser:
            data = [{'ID': c.id, 'Name': c.name, 'User': c.user.username if c.user else ''} for c in queryset]
            columns = ['ID', 'Name', 'User']
        else:
            data = [{'ID': c.id, 'Name': c.name} for c in queryset]
            columns = ['ID', 'Name']
        return self.export_queryset(data, columns, 'Categories')


class StoreViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Store.objects.all().order_by('name')

    def perform_create(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can add stores.")
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can edit stores.")
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            raise PermissionError("Only admins can delete stores.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        top_store = Store.objects.annotate(num_orders=Count('product__order')).order_by('-num_orders').first()
        return Response({
            'count': queryset.count(),
            'top': top_store.name if top_store else None
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.get_queryset()
        if request.user.is_superuser:
            data = [{'ID': s.id, 'Name': s.name, 'Address': s.address, 'User': s.user.username if s.user else ''} for s in queryset]
            columns = ['ID', 'Name', 'Address', 'User']
        else:
            data = [{'ID': s.id, 'Name': s.name, 'Address': s.address} for s in queryset]
            columns = ['ID', 'Name', 'Address']
        return self.export_queryset(data, columns, 'Stores')


class ProductViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.all()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        avg_price = queryset.aggregate(avg_price=Avg('price'))['avg_price'] or 0
        most_ordered = Order.objects.values('product__id', 'product__name').annotate(order_count=Count('product')).order_by('-order_count').first()
        most_ordered_product = {
            'id': most_ordered['product__id'],
            'name': most_ordered['product__name'],
            'order_count': most_ordered['order_count']
        } if most_ordered else None

        return Response({
            'count': queryset.count(),
            'avg_price': round(avg_price, 2),
            'most_ordered': most_ordered_product
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Only administrators can export products"}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        data = [
            {
                'ID': p.id, 'Name': p.name, 'Category': p.category.name if p.category else '',
                'Store': p.store.name if p.store else '', 'Size': p.size, 'Price': p.price,
                'Color': p.color or '', 'Available': 'Yes' if p.is_available() else 'No'
            }
            for p in queryset
        ]
        return self.export_queryset(data, ['ID', 'Name', 'Category', 'Store', 'Size', 'Price', 'Color', 'Available'], 'Products')


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def create(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            age = request.data.get('age')
            is_superuser = request.data.get('is_superuser', False)
            
            if not username or not password:
                return Response({'error': 'username и password обязательны'}, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username уже существует'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                username=username, email=email or '', password=password,
                is_superuser=bool(is_superuser), is_staff=bool(is_superuser)
            )
            
            if age:
                try:
                    UserProfile.objects.get_or_create(user=user, defaults={'age': int(age)})
                except (ValueError, TypeError):
                    pass
            else:
                UserProfile.objects.get_or_create(user=user)
            
            store = Store.objects.first()
            if not store:
                store = Store.objects.create(name='Default Store', address='N/A', user=request.user)
            
            Customer.objects.create(user=user, store=store, first_name=username, last_name='')
            
            return Response(self.get_serializer(user).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            
            if 'username' in request.data:
                user.username = request.data['username']
            if 'email' in request.data:
                user.email = request.data['email']
            if 'password' in request.data and request.data['password']:
                user.set_password(request.data['password'])
            if 'is_superuser' in request.data:
                is_su = request.data['is_superuser']
                user.is_superuser = bool(is_su) if isinstance(is_su, str) else is_su
                user.is_staff = user.is_superuser
            
            user.save()
            
            if 'age' in request.data and request.data['age']:
                try:
                    profile, _ = UserProfile.objects.get_or_create(user=user)
                    profile.age = int(request.data['age'])
                    profile.save()
                except (ValueError, TypeError):
                    pass
            
            return Response(self.get_serializer(user).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        try:
            queryset = self.get_queryset()
            return Response({
                'count': queryset.count(),
                'count_admins': queryset.filter(is_superuser=True).count(),
                'count_users': queryset.filter(is_superuser=False).count(),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        try:
            export_type = request.query_params.get('type', 'excel')
            queryset = self.get_queryset()
            
            if export_type == 'excel':
                return self._export_excel(queryset)
            elif export_type == 'word':
                return self._export_word(queryset)
            else:
                return Response({'error': 'Invalid export type'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _export_excel(self, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Покупатели"
        
        headers = ["ID", "Username", "Email", "Возраст", "Тип"]
        ws.append(headers)
        
        header_fill = PatternFill(start_color="FFD966", end_color="FFD966", fill_type="solid")
        header_font = Font(bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        
        for user in queryset:
            age = None
            try:
                profile = UserProfile.objects.get(user=user)
                age = profile.age
            except UserProfile.DoesNotExist:
                pass
            
            ws.append([
                user.id, user.username, user.email, age or '',
                "Администратор" if user.is_superuser else "Покупатель"
            ])
        
        ws.column_dimensions['A'].width = 8
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 15
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Customers.xlsx"'
        wb.save(response)
        return response
    
    def _export_word(self, queryset):
        doc = Document()
        doc.add_heading('Список покупателей', 0)
        
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Light Grid Accent 1'
        
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "ID"
        hdr_cells[1].text = "Username"
        hdr_cells[2].text = "Email"
        hdr_cells[3].text = "Возраст"
        hdr_cells[4].text = "Тип"
        
        for user in queryset:
            age = None
            try:
                profile = UserProfile.objects.get(user=user)
                age = profile.age
            except UserProfile.DoesNotExist:
                pass
            
            row_cells = table.add_row().cells
            row_cells[0].text = str(user.id)
            row_cells[1].text = user.username
            row_cells[2].text = user.email
            row_cells[3].text = str(age) if age else ''
            row_cells[4].text = "Администратор" if user.is_superuser else "Покупатель"
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename="Customers.docx"'
        doc.save(response)
        return response


class OrderViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.select_related('product', 'customer')
        if self.request.user.is_superuser:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete_order(self, request, pk=None):
        if not request.user.is_superuser:
            return Response({'detail': 'Только администратор может менять статус заказа.'}, status=status.HTTP_403_FORBIDDEN)

        order = self.get_object()
        if order.status == 'sold':
            return Response({'detail': 'Заказ уже завершен.'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import date
        order.status = 'sold'
        order.delivery_date = date.today()
        order.save()

        return Response({'detail': 'Заказ успешно завершен.', 'order': self.get_serializer(order).data})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_sum = qs.aggregate(total=Sum('total_price'))['total'] or 0
        top_customer = qs.values('customer__id', 'customer__first_name').annotate(order_count=Count('order_id')).order_by('-order_count').first()

        return Response({
            'count': qs.count(),
            'total_sum': round(total_sum, 2),
            'topCustomer': {
                'name': top_customer['customer__first_name'] if top_customer else None,
                'order_count': top_customer['order_count'] if top_customer else 0
            }
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Permission denied"}, status=403)

        queryset = self.get_queryset()
        data = [
            {
                'ID': o.order_id, 'Product': o.product.name if o.product else '',
                'Customer': f"{o.customer.first_name} {o.customer.last_name or ''}" if o.customer else '',
                'Quantity': o.quantity, 'Total Price': o.total_price, 'Status': o.get_status_display(),
                'Order Date': o.order_date, 'Delivery Date': o.delivery_date if o.delivery_date else 'Not delivered',
                'User': o.user.username if o.user else ''
            }
            for o in queryset
        ]
        return self.export_queryset(data, ['ID', 'Product', 'Customer', 'Quantity', 'Total Price', 'Status', 'Order Date', 'Delivery Date', 'User'], 'Orders')


class UserProfileViewSet(viewsets.GenericViewSet):
    permission_classes = []

    @action(detail=False, url_path="check-login", methods=['GET'])
    def get_check_login(self, request):
        return Response({'is_authenticated': request.user.is_authenticated})

    @action(detail=False, url_path="login", methods=['POST'])
    def use_login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            otp_code = ''.join(random.choices(string.digits, k=6))
            cache.set(f'otp_pending_{user.username}', {'otp_code': otp_code, 'timestamp': time.time(), 'password': password}, 300)
            print(f'OTP для {user.username}: {otp_code}')
            return Response({
                'is_authenticated': False,
                'username': user.username,
                'email': user.email,
                'otp_sent': True
            })
        return Response({'is_authenticated': False, 'error': 'Неверные учетные данные'}, status=400)

    @action(detail=False, url_path='otp-login', methods=['POST'])
    def otp_login(self, request):
        username = request.data.get('username')
        otp_code = request.data.get('key')
        
        pending_data = cache.get(f'otp_pending_{username}')
        if not pending_data:
            return Response({'success': False, 'error': 'OTP истек или не найден'}, status=400)
        
        if pending_data['otp_code'] != otp_code:
            return Response({'success': False, 'error': 'Неверный OTP код'}, status=400)
        
        if time.time() - pending_data['timestamp'] > 300:
            cache.delete(f'otp_pending_{username}')
            return Response({'success': False, 'error': 'OTP истек'}, status=400)
        
        user = authenticate(username=username, password=pending_data['password'])
        if user:
            login(request, user)
            cache.set(f'otp_good_{user.id}', True, 600)
            cache.delete(f'otp_pending_{username}')
            return Response({'success': True, 'is_authenticated': True})
        
        return Response({'success': False, 'error': 'Ошибка аутентификации'}, status=400)

    @action(detail=False, url_path='otp-status', permission_classes=[IsAuthenticated])
    def get_otp_status(self, request):
        return Response({'otp_good': cache.get(f'otp_good_{request.user.id}', False)})

    @action(detail=False, url_path='info', permission_classes=[IsAuthenticated])
    def get_user_info(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_superuser': request.user.is_superuser
        })