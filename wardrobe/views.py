from django.views.generic import TemplateView
from typing import Any
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import authenticate, login
from django.core.cache import cache
import time
import random
import string
from rest_framework import serializers

from wardrobe.models import Brand, ClothingType, Store, Buyer, Purchase

# -----------------------------
# Главная страница магазина
# -----------------------------
class ShowStoreView(TemplateView):
    template_name = "wardrobe/show_store.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        return context

# -----------------------------
# Права для OTP
# -----------------------------
class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        if not otp_good:
            return False
        otp_timestamp = cache.get(f'otp_timestamp_{request.user.id}', 0)
        if otp_timestamp and (time.time() - otp_timestamp > 600):
            cache.set(f'otp_good_{request.user.id}', False)
            return False
        return True

# -----------------------------
# User + OTP
# -----------------------------
class UserProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    class LoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()

    class OTPSerializer(serializers.Serializer):
        key = serializers.CharField()
        username = serializers.CharField()

    @action(detail=False, url_path="check-login", methods=['GET'], permission_classes=[])
    def get_check_login(self, request):
        return Response({'is_authenticated': self.request.user.is_authenticated})

    @action(detail=False, url_path="login", methods=['POST'], permission_classes=[], serializer_class=LoginSerializer)
    def use_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            otp_code = ''.join(random.choices(string.digits, k=6))
            cache.set(
                f'otp_pending_{user.username}', 
                {'otp_code': otp_code, 'timestamp': time.time(), 'password': serializer.validated_data['password']}, 
                300
            )
            print(f'[v0] OTP код для {user.username}: {otp_code}')
            return Response({'is_authenticated': False,'username': user.username,'email': user.email,'otp_sent': True})
        return Response({'is_authenticated': False,'error': 'Неверные учетные данные'}, status=400)

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer, permission_classes=[])
    def otp_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['key']
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
            login(self.request, user)
            cache.set(f'otp_good_{user.id}', True, 600)
            cache.delete(f'otp_pending_{username}')
            return Response({'success': True, 'is_authenticated': True})
        return Response({'success': False, 'error': 'Ошибка аутентификации'}, status=400)

    @action(detail=False, url_path='otp-status', permission_classes=[IsAuthenticated])
    def get_otp_status(self, request):
        otp_good = cache.get(f'otp_good_{self.request.user.id}', False)
        return Response({'otp_good': otp_good})

    @action(detail=False, url_path='info', permission_classes=[IsAuthenticated])
    def get_user_info(self, request):
        return Response({
            'username': self.request.user.username,
            'email': self.request.user.email,
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name
        })

    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired])
    def page_with_otp_required(self, request):
        return Response({'success': True})
