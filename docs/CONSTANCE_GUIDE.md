# Django Constance 가이드

Django Constance를 사용하여 Admin에서 동적으로 설정값을 관리하는 방법을 설명합니다.

---

## 1. 설치

```bash
pip install django-constance
```

## 2. settings.py 설정

### 2.1 INSTALLED_APPS 등록

```python
INSTALLED_APPS = [
    # unfold 관련 앱들...
    "django.contrib.admin",
    # ...기존 앱들...
    "constance",  # 추가
    # ...프로젝트 앱들...
]
```

### 2.2 백엔드 설정

Database 백엔드를 사용합니다 (별도 Redis 불필요):

```python
# Constance 설정
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
```

> **참고:** Redis를 사용 중이라면 `pip install django-constance[redis]`로 설치 후 Redis 백엔드를 사용할 수 있습니다.

### 2.3 캐시 설정 (선택사항)

DB 백엔드 사용 시 캐시를 연동하면 성능이 향상됩니다:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Constance DB 캐시 (CACHES 설정 후)
CONSTANCE_DATABASE_CACHE_BACKEND = "default"
```

> **주의:** `LocMemCache`는 단일 프로세스 환경에서만 적합합니다. 멀티 프로세스 환경에서는 Memcached나 Redis 캐시를 사용하세요.

## 3. CONSTANCE_CONFIG 정의

### 3.1 기본 구조

```python
from django.utils.translation import gettext_lazy as _

CONSTANCE_CONFIG = {
    "KEY_NAME": (기본값, _("설명"), 타입),
}
```

- 첫 번째 값: 기본값 (Default)
- 두 번째 값: Admin에 표시되는 도움말
- 세 번째 값: 필드 타입 (선택사항, `str`, `int`, `float`, `bool`, `Decimal`, `datetime`, `date`, `time` 등)

### 3.2 실제 예시

```python
from django.utils.translation import gettext_lazy as _

CONSTANCE_CONFIG = {
    # 사이트 기본 설정
    "SITE_NAME": ("My Platform", _("사이트 이름"), str),
    "SITE_DESCRIPTION": ("", _("사이트 설명"), str),
    "MAINTENANCE_MODE": (False, _("점검 모드 활성화"), bool),

    # 사용자 설정
    "MAX_LOGIN_ATTEMPTS": (5, _("최대 로그인 시도 횟수"), int),
    "SESSION_TIMEOUT_MINUTES": (30, _("세션 타임아웃 (분)"), int),
    "ALLOW_REGISTRATION": (True, _("회원가입 허용"), bool),

    # 이메일 설정
    "WELCOME_EMAIL_ENABLED": (True, _("가입 환영 이메일 발송"), bool),
    "SUPPORT_EMAIL": ("support@example.com", _("고객지원 이메일"), str),
}
```

### 3.3 커스텀 필드 (선택지 등)

`CONSTANCE_ADDITIONAL_FIELDS`로 Select, Textarea 등 커스텀 위젯을 사용할 수 있습니다:

```python
CONSTANCE_ADDITIONAL_FIELDS = {
    "language_select": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "django.forms.Select",
            "choices": (
                ("ko", "한국어"),
                ("en", "English"),
                ("ja", "日本語"),
            ),
        },
    ],
    "long_text": [
        "django.forms.fields.CharField",
        {
            "widget": "django.forms.Textarea",
            "widget_kwargs": {"attrs": {"rows": 5}},
        },
    ],
}

CONSTANCE_CONFIG = {
    "DEFAULT_LANGUAGE": ("ko", _("기본 언어"), "language_select"),
    "TERMS_OF_SERVICE": ("", _("이용약관 내용"), "long_text"),
}
```

## 4. Fieldsets (그룹화)

Admin 화면에서 설정을 그룹으로 나누어 표시합니다:

```python
CONSTANCE_CONFIG_FIELDSETS = {
    _("사이트 설정"): {
        "fields": ("SITE_NAME", "SITE_DESCRIPTION", "MAINTENANCE_MODE"),
        "collapse": False,
    },
    _("사용자 설정"): {
        "fields": ("MAX_LOGIN_ATTEMPTS", "SESSION_TIMEOUT_MINUTES", "ALLOW_REGISTRATION"),
        "collapse": False,
    },
    _("이메일 설정"): {
        "fields": ("WELCOME_EMAIL_ENABLED", "SUPPORT_EMAIL"),
        "collapse": True,
    },
}
```

> **주의:** `CONSTANCE_CONFIG_FIELDSETS`에는 `CONSTANCE_CONFIG`의 모든 키가 포함되어야 합니다.

> **참고:** `gettext_lazy`를 fieldset 키에 사용할 경우, `dict` 대신 `tuple` 형태로 작성해야 합니다:

```python
CONSTANCE_CONFIG_FIELDSETS = (
    (
        _("사이트 설정"),
        {
            "fields": ("SITE_NAME", "SITE_DESCRIPTION", "MAINTENANCE_MODE"),
            "collapse": False,
        },
    ),
    (
        _("사용자 설정"),
        {
            "fields": ("MAX_LOGIN_ATTEMPTS", "SESSION_TIMEOUT_MINUTES", "ALLOW_REGISTRATION"),
            "collapse": False,
        },
    ),
)
```

## 5. 마이그레이션

Database 백엔드 사용 시 마이그레이션을 적용합니다:

```bash
python manage.py migrate
```

## 6. 사용법

### 6.1 Python 코드에서 사용

```python
from constance import config

# 읽기
site_name = config.SITE_NAME
is_maintenance = config.MAINTENANCE_MODE

# 쓰기 (코드에서 동적 변경)
config.MAINTENANCE_MODE = True
```

### 6.2 Django 템플릿에서 사용

Context Processor 등록 (settings.py):

```python
TEMPLATES = [
    {
        "OPTIONS": {
            "context_processors": [
                # ...기존 context_processors...
                "constance.context_processors.config",  # 추가
            ],
        },
    },
]
```

템플릿에서 사용:

```html
<h1>{{ config.SITE_NAME }}</h1>

{% if config.MAINTENANCE_MODE %}
    <div class="alert">현재 점검 중입니다.</div>
{% endif %}
```

### 6.3 Serializer / View에서 사용

```python
from constance import config
from rest_framework.views import APIView
from rest_framework.response import Response


class SiteConfigAPIView(APIView):
    def get(self, request):
        return Response({
            "siteName": config.SITE_NAME,
            "maintenanceMode": config.MAINTENANCE_MODE,
        })
```

### 6.4 Signal (값 변경 감지)

```python
from constance.signals import config_updated
from django.dispatch import receiver


@receiver(config_updated)
def constance_updated(sender, key, old_value, new_value, **kwargs):
    if key == "MAINTENANCE_MODE":
        # 점검 모드 변경 시 처리 로직
        pass
```

### 6.5 CLI 명령어

```bash
# 전체 설정 목록 조회
python manage.py constance list

# 특정 값 조회
python manage.py constance get SITE_NAME

# 값 변경
python manage.py constance set SITE_NAME "새 사이트 이름"

# 더 이상 사용하지 않는 키 삭제
python manage.py constance remove_stale_keys
```

## 7. Unfold Admin 사이드바 연동

Unfold 사이드바에 Constance 설정 링크를 추가합니다 (`config/unfold.py`):

```python
{
    "title": _("설정"),
    "icon": "tune",
    "link": reverse_lazy("admin:constance_config_changelist"),
    "permission": "config.views.superuser_permission_callback",
},
```

## 8. 테스트

### 8.1 override_config 데코레이터

```python
from constance.test import override_config


@override_config(MAINTENANCE_MODE=True)
def test_maintenance_mode(self):
    # MAINTENANCE_MODE가 True인 상태로 테스트
    pass
```

### 8.2 pytest에서 사용

```python
import pytest
from constance.test import override_config


@pytest.mark.django_db
@override_config(SITE_NAME="Test Site")
def test_site_name():
    from constance import config
    assert config.SITE_NAME == "Test Site"
```

## 9. 설정값별 적용 가이드

현재 `CONSTANCE_CONFIG`에 정의된 각 설정값을 실제 코드에서 어떻게 활용하는지 정리합니다.

### 9.1 사이트 설정

#### SITE_NAME / SITE_DESCRIPTION

**적용 위치:** 템플릿, API 응답, 이메일 템플릿

```python
# 이메일 템플릿에서 사이트명 사용
from constance import config

subject = f"[{config.SITE_NAME}] 비밀번호 재설정"
```

```html
<!-- 템플릿에서 사용 -->
<title>{{ config.SITE_NAME }}</title>
<meta name="description" content="{{ config.SITE_DESCRIPTION }}">
```

```python
# 프론트엔드에 사이트 정보 제공 API
class SiteConfigAPIView(APIView):
    def get(self, request):
        return Response({
            "siteName": config.SITE_NAME,
            "siteDescription": config.SITE_DESCRIPTION,
        })
```

#### MAINTENANCE_MODE

**적용 위치:** 미들웨어

```python
# config/middleware.py
from constance import config

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin 경로는 점검 모드에서도 접근 허용
        if config.MAINTENANCE_MODE and not request.path.startswith("/admin/"):
            return HttpResponse("현재 점검 중입니다.", status=503)
        return self.get_response(request)
```

```python
# settings.py MIDDLEWARE에 추가
MIDDLEWARE = [
    # ...
    "config.middleware.MaintenanceModeMiddleware",
]
```

### 9.2 사용자 설정

#### MAX_LOGIN_ATTEMPTS

**적용 위치:** 로그인 뷰/API

```python
from constance import config
from django.core.cache import cache

def login(request):
    username = request.data.get("username")
    cache_key = f"login_attempts:{username}"
    attempts = cache.get(cache_key, 0)

    if attempts >= config.MAX_LOGIN_ATTEMPTS:
        return Response({"error": "로그인 시도 횟수를 초과했습니다."}, status=429)

    if not authenticate(username=username, password=request.data.get("password")):
        cache.set(cache_key, attempts + 1, timeout=300)
        return Response({"error": "로그인 실패"}, status=401)

    cache.delete(cache_key)
    # ... 로그인 성공 처리
```

#### SESSION_TIMEOUT_MINUTES

**적용 위치:** 미들웨어 또는 세션 설정

```python
# 미들웨어에서 세션 만료 체크
from constance import config

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get("last_activity")
            now = timezone.now().timestamp()

            if last_activity and (now - last_activity) > config.SESSION_TIMEOUT_MINUTES * 60:
                from django.contrib.auth import logout
                logout(request)

            request.session["last_activity"] = now

        return self.get_response(request)
```

#### ALLOW_REGISTRATION

**적용 위치:** 회원가입 API/뷰

```python
from constance import config

class RegisterAPIView(APIView):
    def post(self, request):
        if not config.ALLOW_REGISTRATION:
            return Response({"error": "현재 회원가입이 중단되었습니다."}, status=403)

        # ... 회원가입 처리
```

### 9.3 이메일 설정

#### WELCOME_EMAIL_ENABLED

**적용 위치:** 회원가입 완료 후 이메일 발송 로직

```python
from constance import config

def on_user_registered(user):
    if config.WELCOME_EMAIL_ENABLED:
        send_welcome_email(user)
```

#### SUPPORT_EMAIL

**적용 위치:** 이메일 템플릿, API 응답

```python
from constance import config

def send_support_info(user):
    send_email(
        to=user.email,
        subject=f"[{config.SITE_NAME}] 문의 안내",
        context={"support_email": config.SUPPORT_EMAIL},
    )
```

```html
<!-- 이메일 템플릿 -->
<p>문의사항은 {{ config.SUPPORT_EMAIL }}로 연락해주세요.</p>
```

### 9.4 적용 요약

| 설정값 | 적용 위치 | 적용 방식 |
|---|---|---|
| `SITE_NAME` | 템플릿, 이메일, API | `config.SITE_NAME` 직접 참조 |
| `SITE_DESCRIPTION` | 메타 태그, API | `config.SITE_DESCRIPTION` 직접 참조 |
| `MAINTENANCE_MODE` | 미들웨어 | 요청마다 체크, `503` 반환 |
| `MAX_LOGIN_ATTEMPTS` | 로그인 뷰 | 캐시와 함께 시도 횟수 제한 |
| `SESSION_TIMEOUT_MINUTES` | 미들웨어 | 세션 마지막 활동 시간 비교 |
| `ALLOW_REGISTRATION` | 회원가입 뷰 | `False`면 `403` 반환 |
| `WELCOME_EMAIL_ENABLED` | 회원가입 후처리 | `False`면 이메일 발송 스킵 |
| `SUPPORT_EMAIL` | 이메일 템플릿, API | 고객지원 이메일 주소로 사용 |

## 10. 체크리스트

### 설정 완료 후 확인사항

- [ ] `django-constance` 패키지 설치
- [ ] `INSTALLED_APPS`에 `"constance"` 추가
- [ ] `CONSTANCE_BACKEND` 설정 (Database 또는 Redis)
- [ ] `CONSTANCE_CONFIG` 정의
- [ ] `CONSTANCE_CONFIG_FIELDSETS` 정의 (모든 키 포함 확인)
- [ ] `python manage.py migrate` 실행
- [ ] Admin에서 Constance 설정 화면 확인
- [ ] Unfold 사이드바에 설정 링크 추가
- [ ] 코드에서 `config.KEY_NAME`으로 접근 테스트
