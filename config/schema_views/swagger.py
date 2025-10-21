"""
Swagger UI Views

드롭다운 네비게이션을 지원하는 커스텀 Swagger UI 뷰들을 제공합니다.
"""

from typing import Any

from drf_spectacular.views import SpectacularSwaggerView


class CustomSwaggerView(SpectacularSwaggerView):
    """Custom Swagger view with additional context"""

    custom_schema_url_name: str | None = None
    custom_title: str | None = None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context.update(
            {
                "current_title": self.custom_title or "API Documentation",
                "schema_url_name": self.custom_schema_url_name or "schema",
            }
        )
        return context


class AllAPIsSwaggerView(CustomSwaggerView):
    """전체 API Swagger 뷰"""

    custom_schema_url_name: str = "schema"
    custom_title: str = "All APIs"


class AppAPIsSwaggerView(CustomSwaggerView):
    """App API Swagger 뷰"""

    custom_schema_url_name: str = "app-schema"
    custom_title: str = "App APIs"


class AdminAPIsSwaggerView(CustomSwaggerView):
    """Admin API Swagger 뷰"""

    custom_schema_url_name: str = "admin-schema"
    custom_title: str = "Admin APIs"


class ExternalAPIsSwaggerView(CustomSwaggerView):
    """External API Swagger 뷰"""

    custom_schema_url_name: str = "external-schema"
    custom_title: str = "External APIs"
