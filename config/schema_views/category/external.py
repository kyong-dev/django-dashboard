"""
External API Schema View

외부 연동 API 스키마 뷰를 제공합니다.
"""

from ..base import CategoryAPISchemaView


class ExternalAPISchemaView(CategoryAPISchemaView):
    """External API 스키마 뷰"""

    category_tags = ["external", "public", "integration"]
    schema_title = "External APIs"
    schema_description = """
## 🌐 외부 연동 API

제3자 서비스 및 시스템 간 연동을 위한 API 모음입니다.
    """
    tag_descriptions = {
        "external": "🌐 외부 연동 API - 제3자 서비스 연동 및 웹훅",
        "public": "🔓 공개 API - 인증 없이 접근 가능한 공개 엔드포인트",
        "integration": "🔗 통합 API - 시스템 간 데이터 동기화 및 연동",
        "external-user": "👤 외부 사용자 API - 외부 사용자 관련 기능",
    }
