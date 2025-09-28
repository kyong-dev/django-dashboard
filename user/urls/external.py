from django.urls import include, path

from rest_framework.routers import DefaultRouter

from ..views.user.external import ExternalUserViewSet

router = DefaultRouter()
router.register(r"users", ExternalUserViewSet, basename="external-users")

urlpatterns = [
    path("api/", include(router.urls)),
]
