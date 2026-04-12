import threading
from typing import Any, Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import activate

from constance import config  # type: ignore[import-untyped]

_thread_locals = threading.local()


def get_current_request() -> HttpRequest | None:
    return getattr(_thread_locals, "request", None)


class DynamicLanguageMiddleware:
    """Constance DEFAULT_LANGUAGE 설정에 따라 요청별 언어를 적용하는 미들웨어"""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        activate(config.DEFAULT_LANGUAGE)
        return self.get_response(request)


class Admin404RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and request.path.startswith("/admin/"):
            return redirect(settings.ADMIN_REDIRECT_URL)
        return response
