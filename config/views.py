import json
from typing import Dict

from django.http import HttpRequest
from django.shortcuts import render

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from config.settings import SERVER_MODE
from config.unfold import color_dict
from user.models import User
from user.serializers import UserListSerializer, UserSerializer
from utils.timezone_utils import get_start_of_today


def index(request):
    return render(request, "index.html")


def environment_callback(request):
    if SERVER_MODE == "LOCAL":
        return ["LOCAL", "danger"]
    elif SERVER_MODE == "DEVELOPMENT":
        return ["DEVELOPMENT", "danger"]
    else:
        return ["PRODUCTION", "success"]


def dashboard_callback(request: HttpRequest, context) -> Dict:
    def get_total_user():
        return User.objects.count()

    bar_chart_data = {
        "data": json.dumps(
            {
                "labels": [
                    "07/22",
                    "07/23",
                    "07/24",
                    "07/25",
                    "07/26",
                    "07/27",
                    "07/28",
                ],
                "datasets": [
                    {
                        "label": "매출",
                        "backgroundColor": "rgba(80, 80, 242, 1)",
                        "data": [
                            20372365,
                            21077579,
                            21577157,
                            25058620,
                            29522239,
                            2496161,
                            24914666,
                        ],
                        "stack": "Stack 0",
                    },
                    {
                        "label": "매입",
                        "backgroundColor": "rgba(196, 209, 197, 1)",
                        "data": [
                            13751566,
                            16303560,
                            31039019,
                            33621116,
                            34660119,
                            0,
                            0,
                        ],
                        "stack": "Stack 1",
                    },
                ],
            }
        ),
        "options": json.dumps({"scales": {"x": {"stacked": True}, "y": {"stacked": True}}}),
    }

    line_chart_data = {
        "data": json.dumps(
            {
                "labels": [
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun",
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun",
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun",
                    "Mon",
                    "Tue",
                    "Wed",
                    "Thu",
                    "Fri",
                    "Sat",
                    "Sun",
                ],
                "datasets": [
                    {
                        "data": [
                            [1, 13],
                            [1, 21],
                            [1, 12],
                            [1, 23],
                            [1, 26],
                            [1, 15],
                            [1, 16],
                            [1, 8],
                            [1, 17],
                            [1, 10],
                            [1, 18],
                            [1, 20],
                            [1, 10],
                            [1, 20],
                            [1, 9],
                            [1, 21],
                            [1, 11],
                            [1, 14],
                            [1, 8],
                            [1, 15],
                            [1, 16],
                            [1, 18],
                            [1, 14],
                            [1, 10],
                            [1, 9],
                            [1, 20],
                            [1, 10],
                        ],
                        "borderColor": f"rgba(47, 51, 234, 0.7)",
                    }
                ],
            }
        ),
        "options": {},
    }

    context.update(
        {
            "cards": [
                {
                    "title": "총 유저",
                    "metric": get_total_user(),
                    "icon": "people",
                    # "footer": "Footer 1",
                },
                {
                    "title": "신규가입",
                    "metric": "1",
                    "icon": "person_add",
                    # "footer": "Footer 2",
                },
                {
                    "title": "인증대기 유저",
                    "metric": "1",
                    "icon": "hourglass",
                    # "footer": "Footer 3",
                },
                {
                    "title": "MAU",
                    "metric": "0",
                    "icon": "monitoring",
                    # "footer": "Footer 3",
                },
            ],
            "table_data": {
                "headers": ["col 1", "col 2"],
                "rows": [
                    ["a", "b"],
                    ["c", "d"],
                ],
            },
            "bar_chart_data": bar_chart_data,
            "line_chart_data": line_chart_data,
            "table_data": {
                "headers": ["유저네임", "이름", "활동", "가입일"],
                "rows": [
                    ["user1", "홍길동", "2024-07-30", "2023-01-01"],
                    ["user2", "김철수", "2024-07-30", "2023-02-15"],
                    ["user3", "이영희", "2024-07-30", "2023-03-20"],
                    ["user4", "박민수", "2024-07-29", "2023-04-10"],
                    ["user5", "최지우", "2024-07-29", "2023-05-05"],
                ],
            },
            "progress_data": [
                {
                    "title": "Daily Exercise",
                    "description": "Completed daily exercise routine",
                    "value": 80,
                },
                {
                    "title": "Reading",
                    "description": "Read 30 pages of a book",
                    "value": 60,
                },
                {
                    "title": "Meditation",
                    "description": "Meditated for 20 minutes",
                    "value": 90,
                },
                {
                    "title": "Coding Practice",
                    "description": "Completed coding challenges",
                    "value": 70,
                },
                {
                    "title": "Water Intake",
                    "description": "Drank 8 glasses of water",
                    "value": 100,
                },
                {"title": "Sleep", "description": "Slept for 8 hours", "value": 85},
            ],
        }
    )
    return context


def user_badge_callback(request):
    start_of_today = get_start_of_today()
    count = User.objects.filter(registered_at__gte=start_of_today).count()
    if count > 0:
        return count
    else:
        return ""


def admin_permission_callback(request):
    return request.user.is_superuser


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

    def get_serializer_class(self):
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
    def force_deactivate(self, request, pk=None):
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
    def system_stats(self, request):
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
