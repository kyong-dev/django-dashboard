from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from .models import User


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Valid User Creation",
            summary="유효한 사용자 생성 예제",
            description="새 사용자를 생성하는 유효한 요청 예제",
            value={"username": "johndoe", "email": "john@example.com", "password": "secure_password123"},
            request_only=True,
        ),
        OpenApiExample(
            "User Response",
            summary="사용자 응답 예제",
            description="사용자 조회/생성 시 반환되는 응답 예제",
            value={
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "is_active": True,
                "is_staff": False,
                "is_superuser": False,
                "registered_at": "2023-01-15T10:30:00Z",
                "deactivated_at": None,
            },
            response_only=True,
        ),
    ]
)
class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 Serializer"""

    password = serializers.CharField(write_only=True, help_text="비밀번호 (생성 시에만 필요)")

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "is_active", "is_staff", "is_superuser", "registered_at", "deactivated_at"]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "registered_at": {"read_only": True},
            "deactivated_at": {"read_only": True},
        }

    def create(self, validated_data):
        """사용자 생성 시 비밀번호 해싱"""
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """사용자 정보 업데이트"""
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """사용자 목록용 간단한 Serializer (비밀번호 제외)"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "is_staff", "registered_at", "deactivated_at"]
        read_only_fields = ["id", "registered_at", "deactivated_at"]
