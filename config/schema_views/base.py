"""
Base Schema View

모든 카테고리별 스키마 뷰의 베이스 클래스를 제공합니다.
"""

import json

from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.views import SpectacularAPIView
from rest_framework.response import Response


class CategoryAPISchemaView(SpectacularAPIView):
    """Base class for category-specific schema views"""

    category_tags = []
    schema_title = ""
    schema_description = """

### 🔗 관련 API 문서
- **[📋 전체 API 문서](/swagger/)** - 모든 API를 한 번에 확인
- **[📱 일반 앱 API](/swagger/app/)** - 앱 서비스 기능
- **[👤 관리자 관련 API](/swagger/admin/)** - 관리자 기능
- **[🌐 외부 연동 API](/swagger/external/)** - 제3자 서비스 연동
"""
    tag_descriptions = {}

    def get(self, request, *args, **kwargs):
        """Override get method to filter by tags"""
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

                if should_include:
                    filtered_paths[path] = filtered_methods

            schema["paths"] = filtered_paths

        # 모든 자식 클래스들의 tag_descriptions를 합침
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
        # 순환 import를 방지하기 위해 동적으로 import
        try:
            from .category.admin import AdminAPISchemaView
            from .category.app import AppAPISchemaView
            from .category.external import ExternalAPISchemaView

            schema_classes = [AppAPISchemaView, AdminAPISchemaView, ExternalAPISchemaView]

            for schema_class in schema_classes:
                if hasattr(schema_class, "tag_descriptions"):
                    combined.update(schema_class.tag_descriptions)
        except ImportError:
            pass  # 초기화 단계에서는 무시

        print(f"Combined tag descriptions: {list(combined.keys())}")
        return combined
