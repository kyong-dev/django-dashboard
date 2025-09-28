"""
App API Schema View

일반 애플리케이션 API 스키마 뷰를 제공합니다.
"""

from ..base import CategoryAPISchemaView


class AppAPISchemaView(CategoryAPISchemaView):
    """App API 스키마 뷰"""

    category_tags = ["app", "user"]
    schema_title = "App APIs"
    schema_description = """
## 📱 일반 애플리케이션 API

사용자가 직접 사용하는 기본 기능들을 제공하는 API 모음입니다.
    """
    tag_descriptions = {"app": "📱 일반 앱 API - 사용자가 직접 사용하는 기본 기능들", "app-user": "👤 사용자 관련 API - 프로필, 인증, 개인정보 관리"}
