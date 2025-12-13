from django.views.generic import TemplateView
from typing import Any
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import authenticate, login, logout as django_logout
from django.core.cache import cache
import time
from rest_framework import serializers
from wardrobe.models import Category, UserProfile
import pyotp
import qrcode
import io
import base64


class ShowStoreView(TemplateView):
    template_name = "wardrobe/show_store.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


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
        return Response({'is_authenticated': request.user.is_authenticated})

    def _generate_qr_code(self, user, totp_key):
        totp = pyotp.TOTP(totp_key)
        provisioning_uri = totp.provisioning_uri(
            name=user.email or user.username,
            issuer_name='Wardrobe'
        )
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        buffer = io.BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_base64 = base64.b64encode(buffer.read()).decode()
        return f'data:image/png;base64,{qr_base64}'


    @action(detail=False, url_path="login", methods=['POST'], permission_classes=[], serializer_class=LoginSerializer)
    def use_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if not profile.totp_key:
                profile.totp_key = pyotp.random_base32()
                profile.save()
            
            qr_code = self._generate_qr_code(user, profile.totp_key)
            
            cache.set(f'otp_pending_{user.username}', {
                'password': serializer.validated_data['password'],
                'timestamp': time.time()
            }, 300)
            
            return Response({
                'is_authenticated': False,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
                'otp_sent': True,
                'qr_code': qr_code,
                'totp_key': profile.totp_key
            })
        return Response({'is_authenticated': False, 'error': 'Неверные учетные данные'}, status=400)

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer, permission_classes=[])
    def otp_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        otp_code = serializer.validated_data['key']
        
        pending_data = cache.get(f'otp_pending_{username}')
        if not pending_data:
            return Response({'success': False, 'error': 'OTP истек или не найден'}, status=400)
        
        if time.time() - pending_data['timestamp'] > 300:
            cache.delete(f'otp_pending_{username}')
            return Response({'success': False, 'error': 'OTP истек'}, status=400)
        
        user = authenticate(username=username, password=pending_data['password'])
        if not user:
            return Response({'success': False, 'error': 'Ошибка аутентификации'}, status=400)
        
        profile = UserProfile.objects.get(user=user)
        totp = pyotp.TOTP(profile.totp_key)
        
        if not totp.verify(otp_code, valid_window=1):
            return Response({'success': False, 'error': 'Неверный OTP код'}, status=400)
        
        login(request, user)
        cache.delete(f'otp_pending_{username}')
        cache.set(f'otp_good_{user.id}', True, 600)
        cache.set(f'otp_timestamp_{user.id}', time.time(), 600)
        
        return Response({'success': True, 'is_authenticated': True, 'is_superuser': user.is_superuser})

    @action(detail=False, url_path='otp-status', permission_classes=[IsAuthenticated])
    def get_otp_status(self, request):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        return Response({'otp_good': otp_good})

    @action(detail=False, url_path='info', permission_classes=[IsAuthenticated])
    def get_user_info(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser
        })

    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired])
    def page_with_otp_required(self, request):
        return Response({'success': True})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='logout')
    def logout(self, request):
        django_logout(request)
        cache.set(f'otp_good_{request.user.id}', False)
        return Response({'success': True})