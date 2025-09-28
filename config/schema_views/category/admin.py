"""
Admin API Schema View

관리자 전용 API 스키마 뷰를 제공합니다.
"""

from ..base import CategoryAPISchemaView


class AdminAPISchemaView(CategoryAPISchemaView):
    """Admin API 스키마 뷰"""

    category_tags = ["admin", "management"]
    schema_title = "Admin APIs"
    schema_description = """
## 🛡️ 관리자 전용 API

시스템 관리자가 사용하는 고급 관리 기능을 제공하는 API 모음입니다.
    """
    tag_descriptions = {
        "admin": "🔧 관리자 API - 시스템 전체 관리 및 모니터링",
        "admin-user": "👥 관리자 사용자 관리 - 사용자 계정 생성/수정/삭제 및 권한 관리",
        "admin-order": "🛒 관리자 주문 관리 - 주문 처리, 상태 변경, 통계 조회",
        "admin-product": "📦 관리자 상품 관리 - 상품 등록, 수정, 재고 관리",
        "management": "⚙️ 시스템 관리 - 설정, 통계, 모니터링 도구",
    }
