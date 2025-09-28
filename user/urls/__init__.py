from django.urls import include, path

from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path("app/", include("user.urls.app")),
    path("admin/", include("user.urls.admin")),
    path("external/", include("user.urls.external")),
]
