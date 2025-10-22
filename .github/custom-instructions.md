# 프로젝트별 커스텀 인스트럭션

> 이 파일은 현재 프로젝트에만 적용되는 특정 규칙과 가이드라인을 정의합니다.

## 프로젝트 정보

- **프로젝트명**: Django Dashboard
- **Django 버전**: 5.2.7
- **Python 버전**: 3.13.5
- **메인 앱**: user, config

## 코딩 규칙

### 1. 타입 힌트 사용
- 모든 함수/메서드에 타입 힌트 추가
- mypy 타입 체크 통과 필수
```python
def create_user(self, username: str, email: str | None = None) -> User:
    pass
```

### 2. Django 모델 패턴
```python
from typing import Any
from django.db import models

class UserManager(BaseUserManager["User"]):
    def create_user(self, username: str, **extra_fields: Any) -> "User":
        # implementation
        pass

class User(AbstractBaseUser):
    objects: UserManager = UserManager()
```

### 3. ViewSet 패턴
```python
from typing import Any
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.serializers import Serializer

class UserViewSet(ModelViewSet):
    def get_queryset(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True)
    
    def get_serializer_class(self) -> type[Serializer]:
        if self.action == "list":
            return UserListSerializer
        return UserSerializer
    
    @action(detail=True, methods=["post"])
    def custom_action(self, request: Any, pk: int | None = None) -> Response:
        # implementation
        pass
```

### 4. Admin 클래스
```python
from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet

class UserAdmin(ModelAdmin):
    @admin.display(description="설명")
    def custom_field(self, obj: User) -> str:
        return obj.username
    
    def custom_action(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        # implementation
        pass
```

## API 문서화

### DRF Spectacular 사용
```python
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    list=extend_schema(tags=["user"], summary="사용자 목록"),
    create=extend_schema(tags=["user"], summary="사용자 생성"),
)
class UserViewSet(ModelViewSet):
    @extend_schema(
        tags=["user"],
        summary="커스텀 액션",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="사용자 ID"
            )
        ],
        responses={200: UserSerializer}
    )
    @action(detail=True, methods=["post"])
    def custom_action(self, request: Any, pk: int | None = None) -> Response:
        pass
```

## 이메일 시스템

### EmailUtils 사용
```python
from utils.email import EmailUtils

# 인증 코드 전송
EmailUtils.send_verification_code(
    to_email="user@example.com",
    username="홍길동",
    verification_code="123456"
)

# 환영 이메일
EmailUtils.send_welcome_email(
    to_email="user@example.com",
    username="홍길동"
)
```

## 환경 변수

### .env 파일 구조
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=dashboard
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Platform
PLATFORM_NAME=Django Dashboard

# AWS S3 (선택사항)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=ap-northeast-2
```

## 테스트 작성

### 기본 패턴
```python
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    def test_user_creation(self) -> None:
        self.assertEqual(self.user.username, "testuser")
        self.assertTrue(self.user.check_password("testpass123"))
    
    def tearDown(self) -> None:
        self.user.delete()
```

## Pre-commit Hooks

현재 설정된 hooks:
1. **isort**: Import 정렬
2. **black**: 코드 포맷팅
3. **mypy**: 타입 체크

```bash
# 수동 실행
python -m pre_commit run --all-files

# 특정 hook만 실행
python -m pre_commit run mypy --all-files
```

## 마이그레이션

### 규칙
1. 모델 변경 후 즉시 마이그레이션 생성
```bash
python manage.py makemigrations
python manage.py migrate
```

2. 마이그레이션 파일 이름 명확하게
```bash
python manage.py makemigrations --name add_user_profile_fields
```

3. 데이터 마이그레이션이 필요한 경우
```bash
python manage.py makemigrations --empty user --name migrate_user_data
```

## 성능 최적화

### QuerySet 최적화
```python
# select_related (ForeignKey, OneToOne)
User.objects.select_related('profile').all()

# prefetch_related (ManyToMany, Reverse ForeignKey)
User.objects.prefetch_related('groups', 'permissions').all()

# only/defer
User.objects.only('username', 'email')
User.objects.defer('password')
```

### 캐싱
```python
from django.core.cache import cache

# 캐시 저장
cache.set('key', value, timeout=300)

# 캐시 조회
value = cache.get('key')

# 캐시 삭제
cache.delete('key')
```

## 보안

### 1. 비밀번호 처리
```python
# 항상 set_password 사용
user.set_password(raw_password)
user.save()

# 비밀번호 확인
user.check_password(raw_password)
```

### 2. 민감한 정보 로깅 금지
```python
# ❌ 나쁜 예
logger.info(f"User password: {password}")

# ✅ 좋은 예
logger.info(f"User {username} logged in")
```

### 3. SQL Injection 방지
```python
# ❌ 나쁜 예
User.objects.raw(f"SELECT * FROM user WHERE username = '{username}'")

# ✅ 좋은 예
User.objects.filter(username=username)
```

## 주의사항

1. **절대 커밋하지 말 것**:
   - `.env` 파일
   - `db.sqlite3` 파일
   - `__pycache__/` 디렉토리
   - `.venv/` 가상환경

2. **항상 가상환경 활성화**:
   ```bash
   source .venv/bin/activate  # macOS/Linux
   ```

3. **의존성 업데이트 시**:
   ```bash
   pip freeze > requirements.txt
   ```

## 문서 참조

- [API 가이드](/docs/API_GUIDE.md)
- [이메일 가이드](/docs/EMAIL_GUIDE.md)
- [메인 README](/docs/README.md)

---

**마지막 업데이트**: 2025-10-22
**담당자**: 개발팀
