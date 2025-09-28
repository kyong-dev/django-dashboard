import threading

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class Admin404RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and request.path.startswith("/admin/"):
            return redirect(settings.ADMIN_REDIRECT_URL)
        return response
