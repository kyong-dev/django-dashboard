from django.contrib.auth import get_user_model
from django.shortcuts import render

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ...models import User
from ...serializers import UserListSerializer, UserSerializer

# Create your views here.


@extend_schema_view(
    list=extend_schema(tags=["app-user"], summary="사용자 목록 조회", description="모든 사용자 목록을 조회합니다. 페이지네이션이 적용됩니다."),
    create=extend_schema(tags=["app-user"], summary="새 사용자 생성", description="새로운 사용자를 생성합니다."),
    retrieve=extend_schema(tags=["app-user"], summary="사용자 상세 조회", description="특정 사용자의 상세 정보를 조회합니다."),
    update=extend_schema(tags=["app-user"], summary="사용자 정보 수정", description="사용자 정보를 전체 수정합니다."),
    partial_update=extend_schema(tags=["app-user"], summary="사용자 정보 부분 수정", description="사용자 정보를 부분적으로 수정합니다."),
    destroy=extend_schema(tags=["app-user"], summary="사용자 비활성화", description="사용자를 삭제합니다."),
)
class UserViewSet(ModelViewSet):
    """
    사용자 관리를 위한 ViewSet

    사용자의 CRUD 작업과 추가적인 기능들을 제공합니다.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """액션에 따라 다른 Serializer 사용"""
        if self.action == "list":
            return UserListSerializer
        return UserSerializer

    def get_queryset(self):
        """활성 사용자만 조회"""
        return User.objects.filter(is_active=True)

    @extend_schema(
        tags=["app-user"],
        summary="사용자 활성화/비활성화",
        description="사용자 계정을 활성화하거나 비활성화합니다.",
        parameters=[OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="사용자 ID")],
        responses={
            200: {"description": "상태 변경 성공", "examples": {"application/json": {"status": "active", "message": "사용자가 활성화되었습니다."}}},
            404: {"description": "사용자를 찾을 수 없습니다."},
        },
    )
    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """사용자 활성화/비활성화 토글"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        status_text = "active" if user.is_active else "inactive"
        message = f'사용자가 {"활성화" if user.is_active else "비활성화"}되었습니다.'

        return Response({"status": status_text, "message": message})

    @extend_schema(
        tags=["app-user"],
        summary="사용자 통계",
        description="사용자 관련 통계 정보를 조회합니다.",
        responses={200: {"description": "통계 조회 성공", "examples": {"application/json": {"total_users": 100, "active_users": 85, "inactive_users": 15, "staff_users": 5, "superuser_count": 1}}}},
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """사용자 통계 정보"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superuser_count = User.objects.filter(is_superuser=True).count()

        return Response({"total_users": total_users, "active_users": active_users, "inactive_users": inactive_users, "staff_users": staff_users, "superuser_count": superuser_count})
