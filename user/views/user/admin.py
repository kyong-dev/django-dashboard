import json
from typing import Any, Dict

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import render

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet

from config.settings import SERVER_MODE
from config.unfold import color_dict
from user.models import User
from user.serializers import UserListSerializer, UserSerializer
from utils.timezone_utils import get_start_of_today


# Admin API ViewSet
@extend_schema_view(
    list=extend_schema(tags=["admin-user"], summary="[관리자] 모든 사용자 조회", description="관리자용 - 비활성 사용자 포함 모든 사용자를 조회합니다."),
    create=extend_schema(tags=["admin-user"], summary="[관리자] 사용자 생성", description="관리자용 - 새로운 사용자를 생성합니다."),
    retrieve=extend_schema(tags=["admin-user"], summary="[관리자] 사용자 상세 조회", description="관리자용 - 특정 사용자의 상세 정보를 조회합니다."),
    update=extend_schema(tags=["admin-user"], summary="[관리자] 사용자 정보 수정", description="관리자용 - 사용자 정보를 전체 수정합니다."),
    partial_update=extend_schema(tags=["admin-user"], summary="[관리자] 사용자 정보 부분 수정", description="관리자용 - 사용자 정보를 부분적으로 수정합니다."),
    destroy=extend_schema(tags=["admin-user"], summary="[관리자] 사용자 삭제", description="관리자용 - 사용자를 삭제합니다."),
)
class AdminUserViewSet(ModelViewSet):
    """
    관리자용 사용자 관리 ViewSet

    비활성 사용자 포함 모든 사용자 관리 기능을 제공합니다.
    """

    queryset = User.objects.all()  # 모든 사용자 (비활성 포함)
    serializer_class = UserSerializer

    def get_serializer_class(self) -> type[Serializer]:
        """액션에 따라 다른 Serializer 사용"""
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    @extend_schema(
        tags=["admin-user"],
        summary="[관리자] 사용자 강제 비활성화",
        description="관리자용 - 사용자를 강제로 비활성화하고 비활성화 시간을 기록합니다.",
        responses={200: {"description": "비활성화 성공", "examples": {"application/json": {"message": "사용자가 비활성화되었습니다.", "deactivated_at": "2023-01-20T14:25:00Z"}}}},
    )
    @action(detail=True, methods=["post"])
    def force_deactivate(self, request: Any, pk: int | None = None) -> Response:
        """관리자용 - 사용자 강제 비활성화"""
        from django.utils import timezone

        user = self.get_object()
        user.is_active = False
        user.deactivated_at = timezone.now()
        user.save()

        return Response({"message": "사용자가 비활성화되었습니다.", "deactivated_at": user.deactivated_at})

    @extend_schema(
        tags=["admin-user"],
        summary="[관리자] 전체 시스템 통계",
        description="관리자용 - 전체 시스템 통계를 조회합니다.",
        responses={
            200: {
                "description": "시스템 통계 조회 성공",
                "examples": {
                    "application/json": {"total_users": 100, "active_users": 85, "inactive_users": 15, "staff_users": 5, "superuser_count": 1, "today_registrations": 3, "this_week_registrations": 12}
                },
            }
        },
    )
    @action(detail=False, methods=["get"])
    def system_stats(self, request: Any) -> Response:
        """관리자용 - 시스템 통계"""
        from datetime import timedelta

        from django.utils import timezone

        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()
        today_registrations = User.objects.filter(registered_at__date=today).count()
        week_registrations = User.objects.filter(registered_at__date__gte=week_ago).count()

        return Response(
            {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "staff_users": staff_users,
                "superuser_count": superuser_count,
                "today_registrations": today_registrations,
                "this_week_registrations": week_registrations,
            }
        )
