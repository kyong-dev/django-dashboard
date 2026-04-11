# API 스키마 버전 관리 가이드

API 스키마를 버전별로 저장하고, Swagger/Redoc에서 확인하며, 신규 엔드포인트에 🆕 NEW 딱지를 자동으로 표시하는 방법을 설명합니다.

---

## 1. 구조

```
static/docs/
├── schema_v1.0.0.yml    # 초기 버전
├── schema_v1.1.0.yml    # 신규 API 추가
├── schema_v1.2.0.yml    # ...
└── schema_v2.0.0.yml    # 메이저 변경
```

---

## 2. 스키마 저장

### 2.1 현재 API 스키마를 버전으로 저장

```bash
python manage.py export_schema 1.0.0
```

### 2.2 기존 버전 덮어쓰기

```bash
python manage.py export_schema 1.0.0 --force
```

### 2.3 버전 네이밍 규칙

[Semantic Versioning](https://semver.org/) 을 따릅니다:

| 변경 | 버전 | 예시 |
|---|---|---|
| 호환되지 않는 변경 | Major (`X.0.0`) | 기존 API 삭제/변경 |
| 신규 기능 추가 | Minor (`1.X.0`) | 새 엔드포인트 추가 |
| 버그 수정/문서 수정 | Patch (`1.0.X`) | 응답 필드 오타 수정 |

---

## 3. 스키마 확인

### 3.1 URL 구조

| URL | 용도 |
|---|---|
| `/api/versions/` | 사용 가능한 버전 목록 (JSON) |
| `/api/versions/1.0.0/schema/` | v1.0.0 스키마 (JSON) |
| `/swagger/versions/1.0.0/` | v1.0.0 Swagger UI |
| `/redoc/versions/1.0.0/` | v1.0.0 Redoc |

### 3.2 기존 Swagger (실시간)

| URL | 용도 |
|---|---|
| `/swagger/` | 전체 API (실시간) |
| `/swagger/app/` | App API |
| `/swagger/admin/` | Admin API |
| `/swagger/external/` | External API |

> 버전별 Swagger UI 상단에 **버전 선택 드롭다운**이 표시됩니다.

---

## 4. 🆕 NEW 딱지

### 4.1 동작 방식

버전별 스키마를 조회하면 **바로 이전 버전과 자동 비교**합니다:

- `v1.1.0` 조회 시 → `v1.0.0`과 비교
- `v1.0.0`에 없던 엔드포인트의 summary에 `🆕` 표시
- description에 `NEW in this version` 라벨 추가

### 4.2 예시

v1.0.0 에 `/api/user/` 만 있고, v1.1.0 에 `/api/user/profile/` 이 추가된 경우:

```
v1.1.0 Swagger UI:

  GET /api/user/              → 사용자 목록 조회
  GET /api/user/profile/      → 🆕 사용자 프로필 조회    ← NEW 딱지
```

### 4.3 첫 번째 버전

이전 버전이 없는 `v1.0.0`에는 NEW 딱지가 표시되지 않습니다.

---

## 5. 워크플로우

### 5.1 신규 API 개발 시

```
1. 새 API 개발 완료
2. 테스트 통과 확인
3. 스키마 저장:
   python manage.py export_schema 1.1.0
4. Swagger에서 확인:
   http://localhost:8000/swagger/versions/1.1.0/
5. NEW 딱지 확인
6. 배포
```

### 5.2 핫픽스 시

```
1. 버그 수정
2. 패치 버전으로 저장:
   python manage.py export_schema 1.1.1
```

---

## 6. 파일 구조

```
config/
├── schema_views/
│   ├── __init__.py
│   ├── base.py              # 카테고리별 스키마 베이스
│   ├── swagger.py           # 커스텀 Swagger 뷰
│   ├── versioned.py         # 버전별 스키마 뷰 (NEW 딱지 로직)
│   └── category/
│       ├── admin.py
│       ├── app.py
│       └── external.py
├── management/
│   └── commands/
│       └── export_schema.py  # 스키마 저장 커맨드
└── urls.py                   # 버전별 URL 등록

templates/
└── drf_spectacular/
    └── swagger-ui.html       # 버전 드롭다운 포함

static/
└── docs/
    ├── schema_v1.0.0.yml     # 저장된 스키마 파일들
    └── schema_v1.1.0.yml
```

---

## 7. API 응답 예시

### GET /api/versions/

```json
{
    "versions": ["1.0.0", "1.1.0", "1.2.0"],
    "latest": "1.2.0"
}
```

### GET /api/versions/1.1.0/schema/

일반 OpenAPI 3.0 스키마에 추가 메타데이터가 포함됩니다:

```json
{
    "info": {
        "title": "Django Dashboard API",
        "version": "1.0.0",
        "x-versions": ["1.0.0", "1.1.0"],
        "x-current-version": "1.1.0",
        "x-previous-version": "1.0.0"
    },
    "paths": {
        "/api/user/profile/": {
            "get": {
                "summary": "🆕 사용자 프로필 조회",
                "description": "**`NEW in this version`**\n\n프로필 정보를 조회합니다."
            }
        }
    }
}
```

---

## 8. 체크리스트

### 신규 버전 저장 시 확인사항

- [ ] API 개발 및 테스트 완료
- [ ] `python manage.py export_schema X.Y.Z` 실행
- [ ] Swagger UI에서 NEW 딱지 확인: `/swagger/versions/X.Y.Z/`
- [ ] Redoc에서도 확인: `/redoc/versions/X.Y.Z/`
- [ ] 버전 목록 확인: `/api/versions/`
- [ ] 스키마 파일 Git 커밋
