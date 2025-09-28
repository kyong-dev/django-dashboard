"""
Schema Views Package

카테고리별로 분리된 API 스키마 뷰들을 제공합니다.
"""

from .base import CategoryAPISchemaView
from .swagger import AllAPIsSwaggerView, AppAPIsSwaggerView, AdminAPIsSwaggerView, ExternalAPIsSwaggerView
from .category.app import AppAPISchemaView
from .category.admin import AdminAPISchemaView
from .category.external import ExternalAPISchemaView

__all__ = [
    "CategoryAPISchemaView",
    "AllAPIsSwaggerView",
    "AppAPIsSwaggerView",
    "AdminAPIsSwaggerView",
    "ExternalAPIsSwaggerView",
    "AppAPISchemaView",
    "AdminAPISchemaView",
    "ExternalAPISchemaView",
]
