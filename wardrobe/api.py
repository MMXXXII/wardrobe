from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Max, Min
from rest_framework import serializers
from .models import Brand, ClothingType, Buyer, Store, Purchase
from .serializers import BrandSerializer, ClothingTypeSerializer, BuyerSerializer, StoreSerializer, PurchaseSerializer

import io
import xlsxwriter
from django.http import FileResponse
from docx import Document

# -----------------------------
# Сериализатор статистики
# -----------------------------
class StatsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    avg = serializers.FloatField()
    max = serializers.IntegerField()
    min = serializers.IntegerField()

# -----------------------------
# Excel экспорт
# -----------------------------
class ExcelExporter:
    def __init__(self, queryset, headers: list[str], fields: list[str], sheet_name="Sheet1", filename="export.xlsx"):
        self.queryset = queryset
        self.headers = headers
        self.fields = fields
        self.sheet_name = sheet_name
        self.filename = filename

    def generate(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.sheet_name)

        # Заголовки
        for col, header in enumerate(self.headers):
            worksheet.write(0, col, header)

        # Данные
        for row, obj in enumerate(self.queryset, start=1):
            for col, field in enumerate(self.fields):
                value = getattr(obj, field, None)

                # ForeignKey или User
                if hasattr(value, 'name'):
                    value = value.name
                elif hasattr(value, 'username'):
                    value = value.username
                else:
                    value = str(value) if value is not None else ""

                worksheet.write(row, col, value)

        workbook.close()
        output.seek(0)
        return FileResponse(
            output,
            as_attachment=True,
            filename=self.filename,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

# -----------------------------
# Word экспорт
# -----------------------------
class WordExporter:
    def __init__(self, queryset, headers: list[str], fields: list[str], filename="export.docx"):
        self.queryset = queryset
        self.headers = headers
        self.fields = fields
        self.filename = filename

    def generate(self):
        doc = Document()
        table = doc.add_table(rows=1, cols=len(self.fields))
        hdr_cells = table.rows[0].cells
        for i, header in enumerate(self.headers):
            hdr_cells[i].text = header

        for obj in self.queryset:
            row_cells = table.add_row().cells
            for i, field in enumerate(self.fields):
                value = getattr(obj, field, None)
                if hasattr(value, 'name'):
                    value = value.name
                elif hasattr(value, 'username'):
                    value = value.username
                else:
                    value = str(value) if value is not None else ""
                row_cells[i].text = value

        f = io.BytesIO()
        doc.save(f)
        f.seek(0)
        return FileResponse(
            f,
            as_attachment=True,
            filename=self.filename,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

# -----------------------------
# Base ViewSet с CRUD, Stats, Excel и Word
# -----------------------------
class BaseModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]
    stats_field = "id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=["GET"], url_path="stats")
    def get_stats(self, request, *args, **kwargs):
        qs = self.get_queryset()
        stats = qs.aggregate(
            count=Count(self.stats_field),
            avg=Avg(self.stats_field),
            max=Max(self.stats_field),
            min=Min(self.stats_field)
        )
        serializer = StatsSerializer(stats)
        return Response(serializer.data)

    def _prepare_export(self):
        """Возвращает queryset, headers и fields с учетом user"""
        if self.request.user.is_superuser:
            qs = super().get_queryset()  # все записи
        else:
            qs = self.get_queryset()      # только свои

        headers, fields = self.get_export_fields()

        # Добавляем user, если есть
        model_fields = [f.name for f in self.queryset.model._meta.fields]
        if 'user' in model_fields:
            headers = ['Пользователь'] + headers
            fields = ['user'] + fields

        return qs, headers, fields

    @action(detail=False, methods=["GET"], url_path="export-excel")
    def export_excel(self, request):
        qs, headers, fields = self._prepare_export()
        exporter = ExcelExporter(
            qs, headers, fields,
            sheet_name=self.__class__.__name__,
            filename=f"{self.__class__.__name__}.xlsx"
        )
        return exporter.generate()

    @action(detail=False, methods=["GET"], url_path="export-word")
    def export_word(self, request):
        qs, headers, fields = self._prepare_export()
        exporter = WordExporter(
            qs, headers, fields,
            filename=f"{self.__class__.__name__}.docx"
        )
        return exporter.generate()

# -----------------------------
# Brand ViewSet
# -----------------------------
class BrandViewSet(BaseModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    stats_field = "id"

    def get_export_fields(self):
        return ["ID", "Название", "Описание"], ["id", "name", "description"]

# -----------------------------
# ClothingType ViewSet
# -----------------------------
class ClothingTypeViewSet(BaseModelViewSet):
    queryset = ClothingType.objects.all()
    serializer_class = ClothingTypeSerializer
    stats_field = "id"

    def get_export_fields(self):
        return ["ID", "Тип одежды"], ["id", "name"]

# -----------------------------
# Buyer ViewSet
# -----------------------------
class BuyerViewSet(BaseModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer
    stats_field = "id"

    def get_export_fields(self):
        return ["ID", "Имя", "Телефон"], ["id", "name", "phone"]

# -----------------------------
# Store ViewSet
# -----------------------------
class StoreViewSet(BaseModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    stats_field = "id"

    def get_export_fields(self):
        return ["ID", "Название", "Адрес"], ["id", "name", "address"]

# -----------------------------
# Purchase ViewSet
# -----------------------------
class PurchaseViewSet(BaseModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    stats_field = "id"

    def get_export_fields(self):
        return ["ID", "Покупатель", "Бренд", "Тип одежды", "Магазин", "Количество", "Дата"], \
               ["id", "buyer", "brand", "clothing_type", "store", "amount", "date"]
