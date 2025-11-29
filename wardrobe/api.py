from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, Max, Min
from django.http import HttpResponse
import io
from openpyxl import Workbook
from docx import Document

from .models import Category, Store, Product, Customer, Order, UserProfile
from .serializers import (
    CategorySerializer, StoreSerializer, ProductSerializer,
    CustomerSerializer, OrderSerializer, UserProfileSerializer
)


class BaseExportMixin:
    """Mixin для экспорта queryset в Excel или Word"""
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
            response = HttpResponse(
                stream,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
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
            response = HttpResponse(
                stream,
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename_base}.docx"'
            return response

        return Response({"error": "Unknown file type"}, status=400)


class CategoryViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_count = qs.count()
        return Response({'count': total_count})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {'ID': c.id, 'Name': c.name, 'User': c.user.username if request.user.is_superuser else '***'}
            for c in qs
        ]
        columns = ['ID', 'Name', 'User'] if request.user.is_superuser else ['ID', 'Name']
        return self.export_queryset(data, columns, 'Categories')


class StoreViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Store.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_count = qs.count()
        return Response({'count': total_count})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {'ID': s.id, 'Name': s.name, 'Address': s.address, 'User': s.user.username if request.user.is_superuser else '***'}
            for s in qs
        ]
        columns = ['ID', 'Name', 'Address', 'User'] if request.user.is_superuser else ['ID', 'Name', 'Address']
        return self.export_queryset(data, columns, 'Stores')


class ProductViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'store')
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_count = qs.count()
        avg_price = qs.aggregate(avg_price=Avg('price'))['avg_price'] or 0
        return Response({'count': total_count, 'avg_price': avg_price})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {
                'ID': p.id,
                'Name': p.name,
                'Category': p.category.name if p.category else '',
                'Store': p.store.name if p.store else '',
                'Price': p.price,
                'User': p.user.username if request.user.is_superuser else '***'
            } for p in qs
        ]
        columns = ['ID', 'Name', 'Category', 'Store', 'Price', 'User'] if request.user.is_superuser else ['ID', 'Name', 'Category', 'Store', 'Price']
        return self.export_queryset(data, columns, 'Products')


class CustomerViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Customer.objects.select_related('store')
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_count = qs.count()
        return Response({'count': total_count})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {
                'ID': c.id,
                'First Name': c.first_name,
                'Last Name': c.last_name,
                'Store': c.store.name if c.store else '',
                'User': c.user.username if request.user.is_superuser else '***'
            } for c in qs
        ]
        columns = ['ID', 'First Name', 'Last Name', 'Store', 'User'] if request.user.is_superuser else ['ID', 'First Name', 'Last Name', 'Store']
        return self.export_queryset(data, columns, 'Customers')


class OrderViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.select_related('product', 'customer')
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_count = qs.count()
        total_sum = qs.aggregate(total=Sum('total_price'))['total'] or 0
        return Response({'count': total_count, 'total_sum': total_sum})

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {
                'ID': o.id,
                'Product': o.product.name if o.product else '',
                'Customer': o.customer.first_name if o.customer else '',
                'Quantity': o.quantity,
                'Total': o.total_price,
                'Status': o.status,
                'User': o.user.username if request.user.is_superuser else '***'
            } for o in qs
        ]
        columns = ['ID', 'Product', 'Customer', 'Quantity', 'Total', 'Status', 'User'] if request.user.is_superuser else ['ID', 'Product', 'Customer', 'Quantity', 'Total', 'Status']
        return self.export_queryset(data, columns, 'Orders')


class UserProfileViewSet(viewsets.ModelViewSet, BaseExportMixin):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = UserProfile.objects.select_related('user')
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    @action(detail=False, methods=['get'])
    def export(self, request):
        qs = self.get_queryset()
        data = [
            {
                'ID': p.id,
                'Username': p.user.username,
                'Email': p.user.email,
                'Age': p.age,
                'Address': p.address
            } for p in qs
        ]
        columns = ['ID', 'Username', 'Email', 'Age', 'Address']
        return self.export_queryset(data, columns, 'UserProfiles')
