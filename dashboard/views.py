import json
from typing import Dict

from django.http import HttpRequest
from django.shortcuts import render

from dashboard.settings import SERVER_MODE
from dashboard.unfold import color_dict
from user.models import User
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
