# 🚀 API 문서화 시스템 가이드

Django REST Framework와 DRF Spectacular를 사용한 API 문서화 시스템입니다.

## 📑 목차

1. [빠른 시작](#-빠른-시작)
2. [태그 기반 분류](#-태그-기반-분류)
3. [ViewSet 문서화](#-viewset-문서화)
4. [URL 구성](#-url-구성)
5. [체크리스트](#-체크리스트)

---

## 🚀 빠른 시작

### API 문서 접근 URL

| 카테고리         | URL                  | 대상 사용자       |
| ---------------- | -------------------- | ----------------- |
| **전체 API**     | `/swagger/`          | 개발자            |
| **App API**      | `/swagger/app/`      | 프론트엔드 개발자 |
| **Admin API**    | `/swagger/admin/`    | 백엔드/관리자     |
| **External API** | `/swagger/external/` | 외부 개발자       |

### 드롭다운 네비게이션

각 Swagger 페이지 상단의 드롭다운으로 카테고리 간 빠른 전환이 가능합니다.

---

## 🏷️ 태그 기반 분류

### 접두사 매칭 시스템

**접두사 기반 자동 분류:**

```python
# admin 태그는 다음을 모두 포함
admin          # 기본 관리자 API
admin-user     # 사용자 관리
admin-order    # 주문 관리
admin-product  # 상품 관리
```

### 카테고리별 태그 매핑

| 카테고리     | 기본 태그             | 확장 태그                 |
| ------------ | --------------------- | ------------------------- |
| **App**      | `app`, `user`         | `app-*`, `user-*`         |
| **Admin**    | `admin`, `management` | `admin-*`, `management-*` |
| **External** | `external`, `public`  | `external-*`, `public-*`  |

### 태그 설명

각 태그에는 이모지와 상세 설명이 자동 추가됩니다:

```python
tag_descriptions = {
    'app': '📱 일반 앱 API - 사용자가 직접 사용하는 기본 기능들',
    'user': '👤 사용자 관련 API - 프로필, 인증, 개인정보 관리',
    'admin': '🔧 관리자 API - 시스템 전체 관리 및 모니터링',
    'admin-user': '👥 관리자 사용자 관리 - 계정 생성/수정/삭제 및 권한 관리',
}
```

---

## 📝 ViewSet 문서화

### 기본 ViewSet 설정

```python
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.viewsets import ModelViewSet

@extend_schema_view(
    list=extend_schema(
        tags=['admin-user'],
        summary='[관리자] 모든 사용자 조회',
        description='관리자용 - 비활성 사용자 포함 모든 사용자를 조회합니다.'
    ),
    create=extend_schema(
        tags=['admin-user'],
        summary='[관리자] 사용자 생성',
        description='관리자용 - 새로운 사용자를 생성합니다.'
    ),
)
class AdminUserViewSet(ModelViewSet):
    """
    👥 관리자용 사용자 관리 ViewSet

    시스템의 모든 사용자를 관리할 수 있는 관리자 전용 API입니다.

    🔐 권한: 관리자 권한 필요
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

### 커스텀 액션 문서화

```python
@extend_schema(
    tags=['admin-user'],
    summary='[관리자] 사용자 강제 비활성화',
    description="""
    **관리자 전용** - 사용자를 강제로 비활성화합니다.

    ### 🎯 사용 목적
    - 문제 사용자 계정 비활성화
    - 임시 계정 정지

    ### 🔄 처리 과정
    1. `is_active`를 `False`로 변경
    2. `deactivated_at` 시간 기록
    3. 사용자 로그인 차단
    """,
    responses={
        200: {
            'description': '✅ 비활성화 성공',
            'examples': {
                'application/json': {
                    'message': '사용자가 비활성화되었습니다.',
                    'user_id': 123
                }
            }
        },
        404: {'description': '❌ 사용자를 찾을 수 없음'},
        403: {'description': '❌ 권한 없음'}
    }
)
@action(detail=True, methods=['post'])
def force_deactivate(self, request, pk=None):
    """사용자 강제 비활성화"""
    user = self.get_object()
    user.deactivate()
    return Response({'message': '사용자가 비활성화되었습니다.'})
```

### APIView 문서화

```python
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

class UserStatsView(APIView):
    @extend_schema(
        tags=['app', 'stats'],
        summary='사용자 통계',
        description='현재 로그인한 사용자의 통계 정보를 반환합니다.',
        responses={200: UserStatsSerializer}
    )
    def get(self, request):
        """사용자 통계 조회"""
        return Response({...})
```

---

## 🔧 URL 구성

### `config/urls.py`

```python
from drf_spectacular.views import SpectacularAPIView
from .schema_views import (
    AppAPISchemaView, AdminAPISchemaView, ExternalAPISchemaView,
    AppAPIsSwaggerView, AdminAPIsSwaggerView, ExternalAPIsSwaggerView
)

schema_patterns = [
    # 스키마 JSON
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/app/', AppAPISchemaView.as_view(), name='app-schema'),
    path('api/schema/admin/', AdminAPISchemaView.as_view(), name='admin-schema'),
    path('api/schema/external/', ExternalAPISchemaView.as_view(), name='external-schema'),

    # Swagger UI
    path('swagger/', AllAPIsSwaggerView.as_view(), name='swagger-ui'),
    path('swagger/app/', AppAPIsSwaggerView.as_view(), name='app-swagger-ui'),
    path('swagger/admin/', AdminAPIsSwaggerView.as_view(), name='admin-swagger-ui'),
    path('swagger/external/', ExternalAPIsSwaggerView.as_view(), name='external-swagger-ui'),
]
```

### 스키마 뷰 구조

```python
# config/schema_views/app.py
class AppAPISchemaView(CategoryAPISchemaView):
    category_tags = ['app', 'user']
    schema_title = 'App APIs'
    schema_description = '일반 애플리케이션 API 문서'
    tag_descriptions = {
        'app': '📱 일반 앱 API',
        'user': '👤 사용자 관련 API'
    }

# config/schema_views/admin.py
class AdminAPISchemaView(CategoryAPISchemaView):
    category_tags = ['admin', 'management']
    schema_title = 'Admin APIs'
    schema_description = '관리자 전용 API 문서'
    tag_descriptions = {
        'admin': '🔧 관리자 API',
        'admin-user': '👥 사용자 관리',
        'admin-order': '🛒 주문 관리'
    }
```

---

## 📋 체크리스트

### API 작성 시 확인 사항

- [ ] **적절한 태그 설정** (`admin-user`, `app`, `external` 등)
- [ ] **명확한 summary와 description** (이모지 권장)
- [ ] **접두사 기반 태그명** (`admin-*`, `app-*` 형태)
- [ ] **응답 예시 제공** (성공/실패 케이스)
- [ ] **권한 정보 명시** (관리자 필요, 인증 필요 등)

### 문서 품질 향상 팁

1. **일관된 태그명**: 접두사 규칙 준수
2. **상세한 설명**: Markdown 형식 활용
3. **실제 예제**: JSON 예제 데이터 포함
4. **에러 처리**: HTTP 상태 코드별 문서화
5. **동기화**: API 변경 시 문서도 업데이트

### 주의사항

- **태그 중복 방지**: 같은 기능을 여러 태그로 분산하지 말 것
- **접두사 일관성**: `admin-`, `app-`, `external-` 패턴 유지
- **설명 동기화**: ViewSet 변경 시 tag_descriptions도 업데이트

---

## 📁 파일 구조

```
config/
├── schema_views/
│   ├── __init__.py
│   ├── base.py              # CategoryAPISchemaView
│   ├── swagger.py           # CustomSwaggerView
│   ├── app.py               # AppAPISchemaView
│   ├── admin.py             # AdminAPISchemaView
│   └── external.py          # ExternalAPISchemaView
├── urls.py
└── settings.py

templates/drf_spectacular/
└── swagger-ui.html          # 커스텀 Swagger 템플릿

user/
├── views/
│   └── user/
│       ├── app.py           # UserViewSet (app/user 태그)
│       ├── admin.py         # AdminUserViewSet (admin-user 태그)
│       └── external.py      # ExternalUserViewSet (external 태그)
└── urls/
    ├── app.py
    ├── admin.py
    └── external.py
```

---

## ⚙️ 설정

### `config/settings.py`

```python
SPECTACULAR_SETTINGS = {
    "TITLE": "Django Dashboard API",
    "DESCRIPTION": "API documentation for Django Dashboard",
    "VERSION": "1.0.0",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "filter": True,
        "docExpansion": "list",
    },
}
```

---

## 🎉 완성된 결과

이 시스템을 통해 얻을 수 있는 것:

1. **카테고리별 분리된 문서** - 사용자 유형에 맞는 맞춤형 문서
2. **자동 태그 분류** - 접두사 매칭으로 유지보수 간편
3. **동적 설명 표시** - 각 카테고리에서 관련 태그만 표시
4. **사용자 친화적 UI** - 드롭다운 네비게이션
5. **중앙 집중식 관리** - 태그 설명 통합 관리

---

**일관되고 전문적인 API 문서를 작성하세요!** 🚀
