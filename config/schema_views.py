import json

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.response import Response


class CategoryAPISchemaView(SpectacularAPIView):
    category_tags = []
    schema_title = ""
    schema_description = ""
    # 각 카테고리별 태그 설명 정의
    tag_descriptions = {}

    def get(self, request, *args, **kwargs):
        print(f"=== {self.__class__.__name__} get() called ===")
        print(f"Target tags: {self.category_tags}")

        generator = SchemaGenerator(patterns=None)
        schema = generator.get_schema(request=request, public=True)

        # 스키마 제목과 설명 변경
        if self.schema_title:
            schema["info"]["title"] = self.schema_title
        if self.schema_description:
            schema["info"]["description"] = self.schema_description

        if self.category_tags:
            filtered_paths = {}

            for path, path_item in schema["paths"].items():
                should_include = False
                filtered_methods = {}

                for method, operation in path_item.items():
                    if method.startswith("_"):
                        continue

                    operation_tags = operation.get("tags", [])
                    print(f"Checking: {method.upper()} {path} - Tags: {operation_tags}")

                    # 접두사 기반 매칭
                    tag_match = False
                    for operation_tag in operation_tags:
                        for target_tag in self.category_tags:
                            if operation_tag == target_tag or operation_tag.startswith(target_tag + "-"):
                                tag_match = True
                                break
                        if tag_match:
                            break

                    if operation_tags and tag_match:
                        should_include = True
                        filtered_methods[method] = operation
                        print(f"✅ INCLUDED: {method.upper()} {path}")
                    else:
                        print(f"❌ EXCLUDED: {method.upper()} {path}")

                if should_include:
                    filtered_paths[path] = filtered_methods

            schema["paths"] = filtered_paths
            print(f"Final filtered paths: {len(filtered_paths)}")

        # 🔥 여기서 모든 자식 클래스들의 tag_descriptions를 합침
        combined_tag_descriptions = self._get_combined_tag_descriptions()

        # 카테고리별 태그 설명 추가
        if combined_tag_descriptions:
            if "tags" not in schema:
                schema["tags"] = []

            # 현재 스키마에 실제로 사용된 태그들만 설명 추가
            used_tags = set()
            for path_item in schema["paths"].values():
                for operation in path_item.values():
                    if isinstance(operation, dict) and "tags" in operation:
                        used_tags.update(operation["tags"])

            # 사용된 태그에 대해서만 설명 추가
            for tag in used_tags:
                if tag in combined_tag_descriptions:
                    schema["tags"].append({"name": tag, "description": combined_tag_descriptions[tag]})

        return Response(schema)

    def _get_combined_tag_descriptions(self):
        """모든 스키마 뷰 클래스의 tag_descriptions를 합쳐서 반환"""
        combined = {}

        # 현재 클래스의 tag_descriptions 추가
        combined.update(self.tag_descriptions)

        # 다른 스키마 뷰 클래스들의 tag_descriptions도 합침
        schema_classes = [AppAPISchemaView, AdminAPISchemaView, ExternalAPISchemaView]

        for schema_class in schema_classes:
            if hasattr(schema_class, "tag_descriptions"):
                combined.update(schema_class.tag_descriptions)

        print(f"Combined tag descriptions: {list(combined.keys())}")
        return combined


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
    custom_schema_url_name = "schema"
    custom_title = "All APIs"


class AppAPIsSwaggerView(CustomSwaggerView):
    custom_schema_url_name = "app-schema"
    custom_title = "App APIs"


class AdminAPIsSwaggerView(CustomSwaggerView):
    custom_schema_url_name = "admin-schema"
    custom_title = "Admin APIs"


class ExternalAPIsSwaggerView(CustomSwaggerView):
    custom_schema_url_name = "external-schema"
    custom_title = "External APIs"


class AppAPISchemaView(CategoryAPISchemaView):
    category_tags = ["app", "user"]
    schema_title = "App APIs"
    schema_description = "일반 애플리케이션 API 문서"
    tag_descriptions = {"app": "📱 일반 앱 API - 사용자가 직접 사용하는 기본 기능들", "user": "👤 사용자 관련 API - 프로필, 인증, 개인정보 관리"}


class AdminAPISchemaView(CategoryAPISchemaView):
    category_tags = ["admin", "management"]
    schema_title = "Admin APIs"
    schema_description = "관리자 전용 API 문서"
    tag_descriptions = {
        "admin": "🔧 관리자 API - 시스템 전체 관리 및 모니터링",
        "admin-user": "👥 관리자 사용자 관리 - 사용자 계정 생성/수정/삭제 및 권한 관리",
        "admin-order": "🛒 관리자 주문 관리 - 주문 처리, 상태 변경, 통계 조회",
        "admin-product": "📦 관리자 상품 관리 - 상품 등록, 수정, 재고 관리",
        "management": "⚙️ 시스템 관리 - 설정, 통계, 모니터링 도구",
    }


class ExternalAPISchemaView(CategoryAPISchemaView):
    category_tags = ["external", "public", "integration"]
    schema_title = "External APIs"
    schema_description = "외부 연동 API 문서"
    tag_descriptions = {
        "external": "🌐 외부 연동 API - 제3자 서비스 연동 및 웹훅",
        "public": "🔓 공개 API - 인증 없이 접근 가능한 공개 엔드포인트",
        "integration": "🔗 통합 API - 시스템 간 데이터 동기화 및 연동",
    }
