from django.views.generic import TemplateView
from typing import Any
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from django.contrib.auth import authenticate, login, logout as django_logout
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework import serializers, status
from wardrobe.models import Category, UserProfile
import pyotp
import qrcode
import io
import base64
import time


class ShowStoreView(TemplateView):
    template_name = "wardrobe/show_store.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class OTPRequired(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        otp_good = cache.get(f"otp_good_{request.user.id}", False)
        if not otp_good:
            return False
        ts = cache.get(f"otp_timestamp_{request.user.id}")
        if ts and time.time() - ts > 600:
            cache.set(f"otp_good_{request.user.id}", False)
            return False
        return True


class UserProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    class LoginSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()

    class OTPSerializer(serializers.Serializer):
        username = serializers.CharField()
        key = serializers.CharField()

    @action(detail=False, methods=["get"], permission_classes=[])
    def check_login(self, request):
        return Response({"is_authenticated": request.user.is_authenticated})

    def _generate_qr(self, user, key):
        totp = pyotp.TOTP(key)
        uri = totp.provisioning_uri(
            name=user.email or user.username,
            issuer_name="Wardrobe"
        )
        qr = qrcode.make(uri)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        buf.seek(0)
        return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[],
        serializer_class=LoginSerializer,
        url_path="login"
    )
    def login_step(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )

        if not user:
            return Response(
                {"is_authenticated": False, "error": "Неверные учетные данные"},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.totp_key:
            profile.totp_key = pyotp.random_base32()
            profile.save()

        try:
            pyotp.TOTP(profile.totp_key).now()
        except Exception:
            profile.totp_key = pyotp.random_base32()
            profile.save()

        qr = self._generate_qr(user, profile.totp_key)

        return Response({
            "is_authenticated": False,
            "otp_sent": True,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "qr_code": qr,
            "totp_key": profile.totp_key
        })

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[],
        serializer_class=OTPSerializer,
        url_path="otp-login"
    )
    def otp_login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(username=serializer.validated_data["username"])
            profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return Response(
                {"success": False, "error": "Пользователь не найден"},
                status=status.HTTP_400_BAD_REQUEST
            )

        totp = pyotp.TOTP(profile.totp_key)
        if not totp.verify(serializer.validated_data["key"]):
            return Response(
                {"success": False, "error": "Неверный OTP код"},
                status=status.HTTP_400_BAD_REQUEST
            )

        login(request, user)
        cache.set(f"otp_good_{user.id}", True, 600)
        cache.set(f"otp_timestamp_{user.id}", time.time(), 600)

        return Response({
            "success": True,
            "is_authenticated": True
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def otp_status(self, request):
        return Response({
            "otp_good": cache.get(f"otp_good_{request.user.id}", False)
        })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def info(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_superuser": u.is_superuser
        })

    @action(detail=False, methods=["get"], permission_classes=[OTPRequired])
    def otp_required(self, request):
        return Response({"success": True})

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        django_logout(request)
        cache.set(f"otp_good_{request.user.id}", False)
        return Response({"success": True})
