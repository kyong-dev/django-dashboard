"""
API 스키마 버전 저장 커맨드

현재 API 스키마를 YAML 파일로 저장하고, 이전 버전 대비 변경사항을 changelog에 기록합니다.

사용법:
    python manage.py export_schema 1.0.0
    python manage.py export_schema 1.1.0
    python manage.py export_schema 1.1.0 --force
"""

from datetime import datetime
import json
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from drf_spectacular.generators import SchemaGenerator
import yaml


def get_path_methods(schema: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """스키마에서 (path, method) -> operation 매핑을 추출합니다."""
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if not method.startswith("x-") and method != "parameters" and isinstance(operation, dict):
                result[(path, method)] = operation
    return result


def get_operation_signature(operation: dict[str, Any]) -> str:
    """operation의 요청/응답 구조를 해시 가능한 문자열로 변환합니다."""
    parts: list[str] = []

    # parameters
    params = operation.get("parameters", [])
    if params:
        param_keys = sorted([f"{p.get('name')}:{p.get('in')}" for p in params if isinstance(p, dict)])
        parts.append(f"params={param_keys}")

    # requestBody schema
    request_body = operation.get("requestBody", {})
    if request_body:
        content = request_body.get("content", {})
        for media_type, media_obj in content.items():
            schema_ref = media_obj.get("schema", {})
            parts.append(f"req:{media_type}={json.dumps(schema_ref, sort_keys=True)}")

    # responses schema
    responses = operation.get("responses", {})
    for status_code, resp in responses.items():
        content = resp.get("content", {}) if isinstance(resp, dict) else {}
        for media_type, media_obj in content.items():
            schema_ref = media_obj.get("schema", {})
            parts.append(f"resp:{status_code}:{media_type}={json.dumps(schema_ref, sort_keys=True)}")

    return "|".join(parts)


def compare_schemas(prev_schema: dict[str, Any], curr_schema: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """두 스키마를 비교하여 추가/수정/삭제된 엔드포인트를 반환합니다."""
    prev_ops = get_path_methods(prev_schema)
    curr_ops = get_path_methods(curr_schema)

    prev_keys = set(prev_ops.keys())
    curr_keys = set(curr_ops.keys())

    added = []
    for path, method in sorted(curr_keys - prev_keys):
        op = curr_ops[(path, method)]
        added.append(
            {
                "method": method.upper(),
                "path": path,
                "summary": op.get("summary", ""),
            }
        )

    removed = []
    for path, method in sorted(prev_keys - curr_keys):
        op = prev_ops[(path, method)]
        removed.append(
            {
                "method": method.upper(),
                "path": path,
                "summary": op.get("summary", ""),
            }
        )

    modified = []
    for key in sorted(prev_keys & curr_keys):
        prev_sig = get_operation_signature(prev_ops[key])
        curr_sig = get_operation_signature(curr_ops[key])
        if prev_sig != curr_sig:
            op = curr_ops[key]
            modified.append(
                {
                    "method": key[1].upper(),
                    "path": key[0],
                    "summary": op.get("summary", ""),
                }
            )

    return {"added": added, "modified": modified, "removed": removed}


class Command(BaseCommand):
    help = "현재 API 스키마를 버전별 YAML 파일로 저장하고 changelog를 생성합니다."

    def add_arguments(self, parser):  # type: ignore[override]
        parser.add_argument(
            "version",
            nargs="?",
            type=str,
            default=None,
            help="스키마 버전 (예: 1.0.0). 생략하면 constance API_VERSION 사용",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="이미 존재하는 파일을 덮어씁니다.",
        )

    def handle(self, *args, **options):  # type: ignore[override]
        from constance import config as constance_config  # type: ignore[import-untyped]

        version: str = options["version"] or constance_config.API_VERSION
        force: bool = options["force"]

        schema_dir = os.path.join(settings.BASE_DIR, "static", "docs")
        os.makedirs(schema_dir, exist_ok=True)

        filepath = os.path.join(schema_dir, f"schema_v{version}.yml")

        if os.path.exists(filepath) and not force:
            raise CommandError(f"schema_v{version}.yml 파일이 이미 존재합니다. " f"덮어쓰려면 --force 옵션을 사용하세요.")

        # 현재 스키마 생성
        generator = SchemaGenerator()
        schema = generator.get_schema(public=True)

        # 스키마 버전 설정
        schema.setdefault("info", {})
        schema["info"]["version"] = version

        # 이전 버전 찾기
        prev_schema = self._find_previous_schema(version, schema_dir)

        # changelog 생성
        changelog_entry: dict[str, Any] = {
            "version": version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "added": [],
            "modified": [],
            "removed": [],
        }

        if prev_schema:
            changes = compare_schemas(prev_schema, schema)
            changelog_entry["added"] = changes["added"]
            changelog_entry["modified"] = changes["modified"]
            changelog_entry["removed"] = changes["removed"]

            # 변경사항 출력
            if changes["added"]:
                self.stdout.write(self.style.SUCCESS(f"\n🆕 추가된 API ({len(changes['added'])}개):"))
                for ep in changes["added"]:
                    self.stdout.write(f"  + {ep['method']} {ep['path']}  {ep['summary']}")

            if changes["modified"]:
                self.stdout.write(self.style.WARNING(f"\n✏️  수정된 API ({len(changes['modified'])}개):"))
                for ep in changes["modified"]:
                    self.stdout.write(f"  ~ {ep['method']} {ep['path']}  {ep['summary']}")

            if changes["removed"]:
                self.stdout.write(self.style.ERROR(f"\n🗑️  삭제된 API ({len(changes['removed'])}개):"))
                for ep in changes["removed"]:
                    self.stdout.write(f"  - {ep['method']} {ep['path']}  {ep['summary']}")

            if not any(changes.values()):
                self.stdout.write(self.style.NOTICE("\n변경사항 없음"))
        else:
            self.stdout.write("이전 버전이 없어 변경사항 비교를 건너뜁니다.")

        # 스키마 저장
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(
                schema,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        # changelog 저장
        self._update_changelog(schema_dir, changelog_entry)

        # constance API_VERSION 업데이트
        if constance_config.API_VERSION != version:
            constance_config.API_VERSION = version
            self.stdout.write(self.style.SUCCESS(f"constance API_VERSION → {version}"))

        self.stdout.write(self.style.SUCCESS(f"\n스키마 v{version}이 저장되었습니다: {filepath}"))

    def _find_previous_schema(self, version: str, schema_dir: str) -> dict[str, Any] | None:
        """현재 버전보다 이전의 가장 최신 스키마를 찾습니다."""
        import re

        pattern = re.compile(r"^schema_v(.+)\.yml$")
        versions: list[str] = []

        for filename in os.listdir(schema_dir):
            match = pattern.match(filename)
            if match:
                versions.append(match.group(1))

        versions.sort(key=lambda v: [int(x) for x in v.split(".")])

        # 현재 버전보다 작은 버전 중 가장 큰 것
        current_parts = [int(x) for x in version.split(".")]
        prev_version = None
        for v in versions:
            v_parts = [int(x) for x in v.split(".")]
            if v_parts < current_parts:
                prev_version = v

        if prev_version is None:
            return None

        prev_filepath = os.path.join(schema_dir, f"schema_v{prev_version}.yml")
        with open(prev_filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _update_changelog(self, schema_dir: str, entry: dict[str, Any]) -> None:
        """changelog.yml 파일을 업데이트합니다."""
        changelog_path = os.path.join(schema_dir, "changelog.yml")

        changelog: list[dict[str, Any]] = []
        if os.path.exists(changelog_path):
            with open(changelog_path, "r", encoding="utf-8") as f:
                changelog = yaml.safe_load(f) or []

        # 같은 버전이 있으면 교체, 없으면 추가
        existing_idx = None
        for i, item in enumerate(changelog):
            if item.get("version") == entry["version"]:
                existing_idx = i
                break

        if existing_idx is not None:
            changelog[existing_idx] = entry
        else:
            changelog.append(entry)

        # 버전 순 정렬
        changelog.sort(key=lambda x: [int(n) for n in x["version"].split(".")])

        with open(changelog_path, "w", encoding="utf-8") as f:
            yaml.dump(
                changelog,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
