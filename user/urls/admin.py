from django.urls import include, path

from rest_framework.routers import DefaultRouter

from ..views.user.admin import AdminUserViewSet

router = DefaultRouter()
router.register(r"users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("", include(router.urls)),
]
# Test comment for GitHub Actions
