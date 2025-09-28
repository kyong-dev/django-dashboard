"""
Swagger UI Views

드롭다운 네비게이션을 지원하는 커스텀 Swagger UI 뷰들을 제공합니다.
"""

from drf_spectacular.views import SpectacularSwaggerView


class CustomSwaggerView(SpectacularSwaggerView):
    """Custom Swagger view with additional context"""

    custom_schema_url_name = None
    custom_title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "current_title": self.custom_title or "API Documentation",
                "schema_url_name": self.custom_schema_url_name or "schema",
            }
        )
        return context


class AllAPIsSwaggerView(CustomSwaggerView):
    """전체 API Swagger 뷰"""

    custom_schema_url_name = "schema"
    custom_title = "All APIs"


class AppAPIsSwaggerView(CustomSwaggerView):
    """App API Swagger 뷰"""

    custom_schema_url_name = "app-schema"
    custom_title = "App APIs"


class AdminAPIsSwaggerView(CustomSwaggerView):
    """Admin API Swagger 뷰"""

    custom_schema_url_name = "admin-schema"
    custom_title = "Admin APIs"


class ExternalAPIsSwaggerView(CustomSwaggerView):
    """External API Swagger 뷰"""

    custom_schema_url_name = "external-schema"
    custom_title = "External APIs"
