"""
Versioned Schema Views

저장된 API 스키마 파일을 버전별로 제공하고,
이전 버전 대비 신규(🆕)/수정(✏️) 엔드포인트에 딱지를 표시합니다.
"""

import os
import re
from typing import Any

from django.conf import settings
from django.urls import reverse

from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView
from rest_framework.response import Response
from rest_framework.views import APIView
import yaml

SCHEMA_DIR = os.path.join(settings.BASE_DIR, "static", "docs")

CATEGORY_TAGS: dict[str, list[str]] = {
    "app": ["app", "user"],
    "admin": ["admin", "management"],
    "external": ["external", "public", "integration"],
}


def get_available_versions() -> list[str]:
    """static/docs/ 에서 사용 가능한 스키마 버전 목록을 반환합니다."""
    versions: list[str] = []
    if not os.path.isdir(SCHEMA_DIR):
        return versions

    pattern = re.compile(r"^schema_v(.+)\.yml$")
    for filename in os.listdir(SCHEMA_DIR):
        match = pattern.match(filename)
        if match:
            versions.append(match.group(1))

    versions.sort(key=lambda v: [int(x) for x in v.split(".")])
    return versions


def get_previous_version(version: str, versions: list[str]) -> str | None:
    """주어진 버전의 바로 이전 버전을 반환합니다."""
    if version not in versions:
        return None
    idx = versions.index(version)
    if idx == 0:
        return None
    return versions[idx - 1]


def load_schema(version: str) -> dict[str, Any] | None:
    """스키마 YAML 파일을 로드합니다."""
    filepath = os.path.join(SCHEMA_DIR, f"schema_v{version}.yml")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_path_methods(schema: dict[str, Any]) -> set[tuple[str, str]]:
    """스키마에서 (path, method) 조합 set을 추출합니다."""
    result: set[tuple[str, str]] = set()
    for path, path_item in schema.get("paths", {}).items():
        for method in path_item:
            if not method.startswith("x-") and method != "parameters":
                result.add((path, method))
    return result


def load_changelog(version: str) -> dict[str, Any] | None:
    """changelog.yml에서 특정 버전의 변경사항을 로드합니다."""
    changelog_path = os.path.join(SCHEMA_DIR, "changelog.yml")
    if not os.path.exists(changelog_path):
        return None
    with open(changelog_path, "r", encoding="utf-8") as f:
        changelog = yaml.safe_load(f) or []
    for entry in changelog:
        if entry.get("version") == version:
            return entry
    return None


def mark_changes(
    schema: dict[str, Any],
    new_endpoints: set[tuple[str, str]],
    modified_endpoints: set[tuple[str, str]],
) -> dict[str, Any]:
    """신규/수정된 엔드포인트에 딱지를 추가합니다."""
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            key = (path, method)
            summary = operation.get("summary", "")
            description = operation.get("description", "")

            if key in new_endpoints and not summary.startswith("🟢"):
                operation["summary"] = f"🟢 {summary}"
                operation["description"] = f"**`NEW in this version`**\n\n{description}"
            elif key in modified_endpoints and not summary.startswith("🟡"):
                operation["summary"] = f"🟡 {summary}"
                operation["description"] = f"**`UPDATED in this version`**\n\n{description}"
    return schema


def filter_schema_by_category(schema: dict[str, Any], category: str) -> dict[str, Any]:
    """스키마에서 특정 카테고리 태그에 해당하는 경로만 필터링합니다."""
    target_tags = CATEGORY_TAGS.get(category, [])
    if not target_tags:
        return schema

    filtered_paths: dict[str, Any] = {}
    for path, path_item in schema.get("paths", {}).items():
        filtered_methods: dict[str, Any] = {}
        for method, operation in path_item.items():
            if not isinstance(operation, dict):
                continue
            operation_tags = operation.get("tags", [])
            for op_tag in operation_tags:
                if any(op_tag == t or op_tag.startswith(f"{t}-") for t in target_tags):
                    filtered_methods[method] = operation
                    break
        if filtered_methods:
            filtered_paths[path] = filtered_methods

    schema["paths"] = filtered_paths
    return schema


class VersionedSchemaAPIView(APIView):
    """버전별 스키마를 제공하고, 신규/수정된 엔드포인트에 딱지를 표시합니다."""

    authentication_classes: list[Any] = []
    permission_classes: list[Any] = []

    def get(self, request: Any, version: str, category: str | None = None) -> Response:
        versions = get_available_versions()
        schema = load_schema(version)

        if schema is None:
            return Response(
                {"error": f"Schema v{version} not found."},
                status=404,
            )

        # changelog에서 변경사항 로드
        changelog = load_changelog(version)

        new_endpoints: set[tuple[str, str]] = set()
        modified_endpoints: set[tuple[str, str]] = set()

        if changelog:
            for ep in changelog.get("added", []):
                new_endpoints.add((ep["path"], ep["method"].lower()))
            for ep in changelog.get("modified", []):
                modified_endpoints.add((ep["path"], ep["method"].lower()))

        if new_endpoints or modified_endpoints:
            schema = mark_changes(schema, new_endpoints, modified_endpoints)

        # 이전 버전이 없을 때는 path-method 비교 폴백
        if not changelog:
            prev_version = get_previous_version(version, versions)
            if prev_version:
                prev_schema = load_schema(prev_version)
                if prev_schema:
                    current_eps = get_path_methods(schema)
                    prev_eps = get_path_methods(prev_schema)
                    fallback_new = current_eps - prev_eps
                    if fallback_new:
                        schema = mark_changes(schema, fallback_new, set())

        # 카테고리 필터링
        category = category or self.kwargs.get("category")
        if category:
            schema = filter_schema_by_category(schema, category)

        # 버전 정보 메타데이터 추가
        prev_version = get_previous_version(version, versions)
        schema.setdefault("info", {})
        schema["info"]["x-versions"] = versions
        schema["info"]["x-current-version"] = version
        if prev_version:
            schema["info"]["x-previous-version"] = prev_version
        if changelog:
            schema["info"]["x-changelog"] = {
                "added": len(changelog.get("added", [])),
                "modified": len(changelog.get("modified", [])),
                "removed": len(changelog.get("removed", [])),
            }

        # 카테고리 링크 추가
        category_links = (
            f"\n\n### 🔗 관련 API 문서 (v{version})\n"
            f"- **[📋 전체 API](/swagger/versions/{version}/)** - 모든 API\n"
            f"- **[📱 App API](/swagger/versions/{version}/app/)** - 앱 서비스\n"
            f"- **[🛠️ Admin API](/swagger/versions/{version}/admin/)** - 관리자\n"
            f"- **[🌐 External API](/swagger/versions/{version}/external/)** - 외부 연동\n"
        )
        description = schema["info"].get("description", "")
        schema["info"]["description"] = description + category_links

        return Response(schema)


class VersionListAPIView(APIView):
    """사용 가능한 스키마 버전 목록을 반환합니다."""

    authentication_classes: list[Any] = []
    permission_classes: list[Any] = []

    def get(self, request: Any) -> Response:
        versions = get_available_versions()
        return Response(
            {
                "versions": versions,
                "latest": versions[-1] if versions else None,
            }
        )


class VersionedSwaggerView(SpectacularSwaggerView):
    """버전별 Swagger UI 뷰 (카테고리 필터 지원)"""

    def _get_schema_url(self, request: Any) -> str:
        version = self.kwargs.get("version", "")
        category = self.kwargs.get("category")
        if category:
            return reverse(
                "versioned-category-schema",
                kwargs={"version": version, "category": category},
            )
        return reverse("versioned-schema", kwargs={"version": version})

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # url_name 기반 reverse를 우회하기 위해 직접 schema_url 설정
        context = super().get_context_data(**kwargs)
        version = self.kwargs.get("version", "")
        category = self.kwargs.get("category")
        versions = get_available_versions()
        context.update(
            {
                "current_version": version,
                "current_category": category or "",
                "available_versions": versions,
                "is_versioned": True,
                "schema_url": self._get_schema_url(self.request),
            }
        )
        return context


class VersionedRedocView(SpectacularRedocView):
    """버전별 Redoc 뷰 (카테고리 필터 지원)"""

    def _get_schema_url(self, request: Any) -> str:
        version = self.kwargs.get("version", "")
        category = self.kwargs.get("category")
        if category:
            return reverse(
                "versioned-category-schema",
                kwargs={"version": version, "category": category},
            )
        return reverse("versioned-schema", kwargs={"version": version})

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        version = self.kwargs.get("version", "")
        category = self.kwargs.get("category")
        versions = get_available_versions()
        context.update(
            {
                "current_version": version,
                "current_category": category or "",
                "available_versions": versions,
                "is_versioned": True,
                "schema_url": self._get_schema_url(self.request),
            }
        )
        return context
