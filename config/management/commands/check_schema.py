"""
API 스키마 변경 감지 커맨드

현재 코드의 API 스키마와 마지막 저장된 스키마를 비교하여 변경사항이 있으면 경고합니다.
pre-commit hook에서 사용됩니다.

사용법:
    python manage.py check_schema
"""

import json
import os
import re
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from drf_spectacular.generators import SchemaGenerator
import yaml


def get_operation_signature(operation: dict[str, Any]) -> str:
    """operation의 요청/응답 구조를 비교 가능한 문자열로 변환합니다."""
    parts: list[str] = []

    params = operation.get("parameters", [])
    if params:
        param_keys = sorted([f"{p.get('name')}:{p.get('in')}" for p in params if isinstance(p, dict)])
        parts.append(f"params={param_keys}")

    request_body = operation.get("requestBody", {})
    if request_body:
        content = request_body.get("content", {})
        for media_type, media_obj in content.items():
            schema_ref = media_obj.get("schema", {})
            parts.append(f"req:{media_type}={json.dumps(schema_ref, sort_keys=True)}")

    responses = operation.get("responses", {})
    for status_code, resp in responses.items():
        content = resp.get("content", {}) if isinstance(resp, dict) else {}
        for media_type, media_obj in content.items():
            schema_ref = media_obj.get("schema", {})
            parts.append(f"resp:{status_code}:{media_type}={json.dumps(schema_ref, sort_keys=True)}")

    return "|".join(parts)


class Command(BaseCommand):
    help = "현재 API 스키마와 마지막 저장 버전을 비교하여 변경사항을 감지합니다."

    def handle(self, *args: Any, **options: Any) -> None:
        schema_dir = os.path.join(settings.BASE_DIR, "static", "docs")

        # 최신 저장 스키마 찾기
        latest_schema = self._find_latest_schema(schema_dir)
        if latest_schema is None:
            self.stdout.write(self.style.NOTICE("저장된 스키마가 없습니다. 건너뜁니다."))
            return

        # 현재 스키마 생성
        generator = SchemaGenerator()
        current_schema = generator.get_schema(public=True)

        # 비교
        prev_ops = self._get_path_methods(latest_schema)
        curr_ops = self._get_path_methods(current_schema)

        prev_keys = set(prev_ops.keys())
        curr_keys = set(curr_ops.keys())

        added = sorted(curr_keys - prev_keys)
        removed = sorted(prev_keys - curr_keys)

        modified = []
        for key in sorted(prev_keys & curr_keys):
            prev_sig = get_operation_signature(prev_ops[key])
            curr_sig = get_operation_signature(curr_ops[key])
            if prev_sig != curr_sig:
                modified.append(key)

        if not added and not modified and not removed:
            self.stdout.write(self.style.SUCCESS("API 스키마 변경사항 없음 ✅"))
            return

        # 변경사항 출력
        self.stderr.write(self.style.ERROR("\n⚠️  API 스키마가 변경되었지만 아직 저장되지 않았습니다!\n"))

        if added:
            self.stderr.write(self.style.SUCCESS(f"🆕 추가 ({len(added)}개):"))
            for path, method in added:
                summary = curr_ops[(path, method)].get("summary", "")
                self.stderr.write(f"  + {method.upper()} {path}  {summary}")

        if modified:
            self.stderr.write(self.style.WARNING(f"✏️  수정 ({len(modified)}개):"))
            for path, method in modified:
                summary = curr_ops[(path, method)].get("summary", "")
                self.stderr.write(f"  ~ {method.upper()} {path}  {summary}")

        if removed:
            self.stderr.write(self.style.ERROR(f"🗑️  삭제 ({len(removed)}개):"))
            for path, method in removed:
                summary = prev_ops[(path, method)].get("summary", "")
                self.stderr.write(f"  - {method.upper()} {path}  {summary}")

        self.stderr.write(self.style.ERROR("\n다음 명령어로 스키마를 저장하세요:" "\n  python manage.py export_schema <version>\n"))
        raise SystemExit(1)

    def _find_latest_schema(self, schema_dir: str) -> dict[str, Any] | None:
        """가장 최신 스키마를 로드합니다."""
        if not os.path.isdir(schema_dir):
            return None

        pattern = re.compile(r"^schema_v(.+)\.yml$")
        versions: list[str] = []

        for filename in os.listdir(schema_dir):
            match = pattern.match(filename)
            if match:
                versions.append(match.group(1))

        if not versions:
            return None

        versions.sort(key=lambda v: [int(x) for x in v.split(".")])
        latest = versions[-1]

        filepath = os.path.join(schema_dir, f"schema_v{latest}.yml")
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _get_path_methods(self, schema: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
        """스키마에서 (path, method) -> operation 매핑을 추출합니다."""
        result: dict[tuple[str, str], dict[str, Any]] = {}
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                if not method.startswith("x-") and method != "parameters" and isinstance(operation, dict):
                    result[(path, method)] = operation
        return result
