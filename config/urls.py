"""
URL configuration for dashboard project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

import debug_toolbar
from drf_spectacular.views import SpectacularRedocView
from rest_framework import routers

from .schema_views import *
from .schema_views.versioned import VersionedRedocView, VersionedSchemaAPIView, VersionedSwaggerView, VersionListAPIView

router = routers.DefaultRouter()
# AdminUserViewSet은 이제 user/views/user/admin.py로 이동됨


def index(request):
    return redirect("admin:index")


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        # Complete API schema
        path("api/schema/", CategoryAPISchemaView.as_view(), name="schema"),
        path("swagger/", AllAPIsSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
        # App API Documentation
        path("api/schema/app/", AppAPISchemaView.as_view(), name="app-schema"),
        path("swagger/app/", AppAPIsSwaggerView.as_view(), name="app-swagger-ui"),
        path("api/schema/app/redoc/", VersionedRedocView.as_view(), name="app-redoc"),
        # Admin API Documentation
        path("api/schema/admin/", AdminAPISchemaView.as_view(), name="admin-schema"),
        path("swagger/admin/", AdminAPIsSwaggerView.as_view(url_name="admin-schema"), name="admin-swagger-ui"),
        path("api/schema/admin/redoc/", SpectacularRedocView.as_view(url_name="admin-schema"), name="admin-redoc"),
        # External API Documentation
        path("api/schema/external/", ExternalAPISchemaView.as_view(), name="external-schema"),
        path("swagger/external/", ExternalAPIsSwaggerView.as_view(url_name="external-schema"), name="external-swagger-ui"),
        path("api/schema/external/redoc/", SpectacularRedocView.as_view(url_name="external-schema"), name="external-redoc"),
        # Versioned Schema
        path("api/versions/", VersionListAPIView.as_view(), name="version-list"),
        path("api/versions/<str:version>/schema/", VersionedSchemaAPIView.as_view(), name="versioned-schema"),
        path("swagger/versions/<str:version>/", VersionedSwaggerView.as_view(), name="versioned-swagger"),
        path("redoc/versions/<str:version>/", VersionedRedocView.as_view(), name="versioned-redoc"),
    ]
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        path("silk/", include("silk.urls", namespace="silk")),
    ]
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
