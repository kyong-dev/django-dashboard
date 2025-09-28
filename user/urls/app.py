from django.urls import include, path

from rest_framework.routers import DefaultRouter

from ..views.user.app import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="app-users")

urlpatterns = [
    path("api/", include(router.urls)),
]
