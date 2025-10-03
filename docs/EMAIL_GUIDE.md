# 📧 이메일 시스템 완벽 가이드

Django 프로젝트의 이메일 전송을 위한 통합 유틸리티 시스템입니다.

## 📑 목차

1. [빠른 시작](#-빠른-시작)
2. [기본 사용법](#-기본-사용법)
3. [동적 설정](#-동적-설정)
4. [API 메서드](#-api-메서드)
5. [View 통합](#-view-통합)
6. [테스트](#-테스트)
7. [설정 가이드](#-설정-가이드)
8. [템플릿 커스터마이징](#-템플릿-커스터마이징)

---

## 🚀 빠른 시작

### 📦 포함된 템플릿

| 템플릿             | 메서드                                 | 용도                             |
| ------------------ | -------------------------------------- | -------------------------------- |
| 🔢 인증번호        | `send_verification_code()`             | 이메일 인증번호 발송 (5분 유효)  |
| 👋 회원가입 환영   | `send_welcome_email()`                 | 신규 회원 환영 메시지            |
| 🔐 비밀번호 재설정 | `send_password_reset_email()`          | 비밀번호 재설정 링크 (30분 유효) |
| ✅ 비밀번호 변경   | `send_password_changed_notification()` | 비밀번호 변경 완료 알림          |
| 😢 계정 비활성화   | `send_account_deactivation_email()`    | 계정 비활성화 안내               |
| 🔔 로그인 알림     | `send_login_notification()`            | 새로운 로그인 감지 (보안)        |
| 🎨 커스텀          | `send_custom_email()`                  | 사용자 정의 템플릿               |

### 30초 예제

```python
from utils.email import EmailUtils

# 인증번호 발송
result = EmailUtils.send_verification_code("user@example.com")
print(result['code'])  # "670306"

# 인증번호 검증
is_valid = EmailUtils.verify_code("user@example.com", "670306")

# 회원가입 환영
EmailUtils.send_welcome_email(
    email="user@example.com",
    username="kyong",
    full_name="경섭 공"
)
```

---

## 📝 기본 사용법

### 1. EmailUtils 임포트

```python
from utils.email import EmailUtils
```

### 2. 이메일 인증번호 발송

```python
# 자동 6자리 인증번호 생성
result = EmailUtils.send_verification_code("user@example.com")

print(result['success'])  # True/False
print(result['code'])     # "123456"
print(result['message'])  # "인증번호가 발송되었습니다."

# 커스텀 인증번호 사용
result = EmailUtils.send_verification_code(
    email="user@example.com",
    code="999888"
)
```

### 3. 인증번호 검증

```python
is_valid = EmailUtils.verify_code("user@example.com", "123456")

if is_valid:
    print("✅ 인증 성공!")
else:
    print("❌ 인증 실패 - 코드가 틀렸거나 만료되었습니다.")
```

### 4. 회원가입 환영 이메일

```python
success = EmailUtils.send_welcome_email(
    email="newuser@example.com",
    username="kyong",
    full_name="경섭 공"  # 선택사항
)
```

### 5. 비밀번호 재설정

```python
import uuid

# 재설정 토큰 생성
reset_token = str(uuid.uuid4())

# 이메일 발송
success = EmailUtils.send_password_reset_email(
    email="user@example.com",
    reset_token=reset_token,
    username="kyong"
)

# 나중에 토큰 검증
is_valid = EmailUtils.verify_password_reset_token(
    email="user@example.com",
    token=reset_token
)
```

### 6. 비밀번호 변경 알림

```python
success = EmailUtils.send_password_changed_notification(
    email="user@example.com",
    username="kyong"
)
```

### 7. 계정 비활성화 알림

```python
success = EmailUtils.send_account_deactivation_email(
    email="user@example.com",
    username="kyong"
)
```

### 8. 로그인 알림 (보안)

```python
success = EmailUtils.send_login_notification(
    email="user@example.com",
    username="kyong",
    ip_address="123.456.78.90",
    device_info="MacBook Air (macOS 14.0)"
)
```

### 9. 커스텀 템플릿 이메일

```python
# templates/emails/custom_template.html 파일 생성 후
success = EmailUtils.send_custom_email(
    email="user@example.com",
    subject="커스텀 이메일 제목",
    template_name="custom_template.html",
    context={
        'username': 'kyong',
        'custom_data': 'some value'
    }
)
```

---

## ⚙️ 동적 설정

### 플랫폼 이름 동적 처리

**`.env` 파일에서 설정:**

```env
# 플랫폼 이름 (기본값: "플랫폼")
PLATFORM_NAME=플랫폼이름
```

**결과:**

- 이메일 제목: `[플랫폼이름] 이메일 인증번호 안내`
- 이메일 헤더: `플랫폼이름`
- 이메일 푸터: `© 2025 플랫폼이름. All rights reserved.`

### 년도 자동 렌더링

- Django 템플릿 태그 `{% now "Y" %}` 사용
- 서버 사이드 렌더링으로 이메일 클라이언트 호환성 보장
- 매년 자동으로 업데이트됨

### 적용 범위

✅ **모든 이메일에 자동 적용:**

- 이메일 제목
- 이메일 헤더
- 이메일 본문
- 이메일 푸터
- 현재 년도

---

## 📋 API 메서드

### `send_verification_code(email, code=None)`

```python
result = EmailUtils.send_verification_code("user@example.com")
# Returns: {'success': bool, 'code': str, 'message': str}
```

- **설명**: 6자리 인증번호를 이메일로 발송
- **캐시 만료**: 5분 (300초)
- **반환값**: 딕셔너리 (성공 여부, 코드, 메시지)

### `verify_code(email, code)`

```python
is_valid = EmailUtils.verify_code("user@example.com", "123456")
# Returns: bool
```

- **설명**: 인증번호 검증 (검증 성공 시 자동 삭제)
- **반환값**: True/False

### `send_welcome_email(email, username, full_name=None)`

```python
success = EmailUtils.send_welcome_email(
    email="user@example.com",
    username="kyong",
    full_name="경섭 공"
)
# Returns: bool
```

- **설명**: 회원가입 환영 이메일
- **반환값**: 성공 여부

### `send_password_reset_email(email, reset_token, username)`

```python
success = EmailUtils.send_password_reset_email(
    email="user@example.com",
    reset_token="uuid-token",
    username="kyong"
)
# Returns: bool
```

- **설명**: 비밀번호 재설정 링크 이메일
- **캐시 만료**: 30분 (1800초)
- **반환값**: 성공 여부

### `verify_password_reset_token(email, token)`

```python
is_valid = EmailUtils.verify_password_reset_token(
    email="user@example.com",
    token="uuid-token"
)
# Returns: bool
```

- **설명**: 비밀번호 재설정 토큰 검증
- **반환값**: True/False

### `send_password_changed_notification(email, username)`

```python
success = EmailUtils.send_password_changed_notification(
    email="user@example.com",
    username="kyong"
)
# Returns: bool
```

- **설명**: 비밀번호 변경 완료 알림
- **반환값**: 성공 여부

### `send_account_deactivation_email(email, username)`

```python
success = EmailUtils.send_account_deactivation_email(
    email="user@example.com",
    username="kyong"
)
# Returns: bool
```

- **설명**: 계정 비활성화 알림
- **반환값**: 성공 여부

### `send_login_notification(email, username, ip_address=None, device_info=None)`

```python
success = EmailUtils.send_login_notification(
    email="user@example.com",
    username="kyong",
    ip_address="127.0.0.1",
    device_info="Chrome"
)
# Returns: bool
```

- **설명**: 새로운 로그인 감지 알림 (보안)
- **반환값**: 성공 여부

### `send_custom_email(email, subject, template_name, context)`

```python
success = EmailUtils.send_custom_email(
    email="user@example.com",
    subject="제목",
    template_name="custom.html",
    context={'key': 'value'}
)
# Returns: bool
```

- **설명**: 커스텀 템플릿으로 이메일 발송
- **반환값**: 성공 여부

---

## 🔌 View 통합

### Django REST Framework ViewSet

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.email import EmailUtils
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['post'])
    def send_verification(self, request):
        """이메일 인증번호 발송 API"""
        email = request.data.get('email')

        result = EmailUtils.send_verification_code(email)

        return Response({
            'success': result['success'],
            'message': result['message']
        }, status=status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify_code(self, request):
        """인증번호 검증 API"""
        email = request.data.get('email')
        code = request.data.get('code')

        is_valid = EmailUtils.verify_code(email, code)

        return Response({
            'valid': is_valid,
            'message': '인증되었습니다.' if is_valid else '인증번호가 올바르지 않습니다.'
        })

    def create(self, request):
        """회원가입 시 환영 이메일 발송"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 환영 이메일 발송
        EmailUtils.send_welcome_email(
            email=user.email,
            username=user.username,
            full_name=user.get_full_name()
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reset_password_request(self, request):
        """비밀번호 재설정 요청"""
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)

            # 재설정 토큰 생성
            import uuid
            reset_token = str(uuid.uuid4())

            # 이메일 발송
            success = EmailUtils.send_password_reset_email(
                email=email,
                reset_token=reset_token,
                username=user.username
            )

            return Response({
                'success': success,
                'message': '비밀번호 재설정 링크가 이메일로 전송되었습니다.'
            })

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': '해당 이메일로 등록된 사용자가 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """비밀번호 변경 후 알림"""
        user = self.get_object()

        # 비밀번호 변경 로직...
        # user.set_password(new_password)
        # user.save()

        # 변경 알림 이메일
        EmailUtils.send_password_changed_notification(
            email=user.email,
            username=user.username
        )

        return Response({'message': '비밀번호가 변경되었습니다.'})
```

### 실전 예제: 회원가입 플로우

```python
# 1. 이메일 인증번호 발송
result = EmailUtils.send_verification_code(email)

# 2. 사용자가 코드 입력 → 검증
is_valid = EmailUtils.verify_code(email, user_input_code)

# 3. 검증 성공 후 회원 생성
if is_valid:
    user = User.objects.create_user(...)

    # 4. 환영 이메일 발송
    EmailUtils.send_welcome_email(
        email=user.email,
        username=user.username,
        full_name=user.get_full_name()
    )
```

### 비밀번호 재설정 플로우

```python
# 1. 재설정 요청
import uuid
reset_token = str(uuid.uuid4())

EmailUtils.send_password_reset_email(
    email=user.email,
    reset_token=reset_token,
    username=user.username
)

# 2. 사용자가 이메일 링크 클릭 → 토큰 검증
is_valid = EmailUtils.verify_password_reset_token(email, token)

# 3. 검증 성공 후 비밀번호 변경
if is_valid:
    user.set_password(new_password)
    user.save()

    # 4. 변경 완료 알림
    EmailUtils.send_password_changed_notification(
        email=user.email,
        username=user.username
    )
```

---

## 🧪 테스트

### 전체 테스트 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# 모든 이메일 타입 테스트
python test_email_utils.py
```

### 개별 테스트

```bash
# 인증번호 이메일
python test_email_utils.py verification

# 회원가입 환영 이메일
python test_email_utils.py welcome

# 비밀번호 재설정 이메일
python test_email_utils.py reset
```

### Django 테스트

```python
from django.test import TestCase
from django.core import mail
from utils.email import EmailUtils

class EmailUtilsTests(TestCase):

    def test_send_verification_code(self):
        """인증번호 이메일 발송 테스트"""
        result = EmailUtils.send_verification_code("test@example.com")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['code']), 6)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(result['code'], mail.outbox[0].body)

    def test_verify_code(self):
        """인증번호 검증 테스트"""
        # 발송
        result = EmailUtils.send_verification_code("test@example.com")
        code = result['code']

        # 올바른 코드로 검증
        self.assertTrue(EmailUtils.verify_code("test@example.com", code))

        # 이미 사용된 코드로 재검증 (실패해야 함)
        self.assertFalse(EmailUtils.verify_code("test@example.com", code))
```

---

## ⚙️ 설정 가이드

### `.env` 파일 설정

```env
# 플랫폼 이름
PLATFORM_NAME=플랫폼이름

# SMTP 설정
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com

# 프론트엔드 URL (비밀번호 재설정 링크용)
FRONTEND_URL=http://localhost:3000
```

### Gmail 사용 시

1. **앱 비밀번호 생성**

   - Google 계정 → 보안 → 2단계 인증 활성화
   - 앱 비밀번호 생성하여 `EMAIL_HOST_PASSWORD`에 설정

2. **포트 설정**
   - 포트 587: `EMAIL_USE_TLS=True`, `EMAIL_USE_SSL=False`
   - 포트 465: `EMAIL_USE_SSL=True`, `EMAIL_USE_TLS=False`

### `config/settings.py`

```python
# 이메일 설정
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# 플랫폼 이름
PLATFORM_NAME = env("PLATFORM_NAME", default="플랫폼")

# 프론트엔드 URL
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")
```

---

## 🎨 템플릿 커스터마이징

### 기본 레이아웃 수정

`templates/emails/base.html` 수정:

```html
<div class="email-header">
  <h1>{{ platform_name }}</h1>
</div>

<div class="email-footer">
  <p>본 메일은 발신 전용입니다.</p>
  <p>&copy; {% now "Y" %} {{ platform_name }}. All rights reserved.</p>
</div>
```

### 새로운 템플릿 생성

`templates/emails/my_custom_email.html`:

```html
{% extends "emails/base.html" %} {% block content %}
<h2>커스텀 이메일 제목</h2>

<p>안녕하세요, <strong>{{ username }}</strong>님!</p>

<div class="info-box">
  <p>여기에 내용을 작성하세요.</p>
</div>

<div class="warning-box">
  <strong>⚠️ 주의사항</strong>
  <ul>
    <li>항목 1</li>
    <li>항목 2</li>
  </ul>
</div>

<div style="text-align: center;">
  <a href="{{ action_url }}" class="button"> 버튼 텍스트 </a>
</div>
{% endblock %}
```

### 사용 가능한 CSS 클래스

- `.info-box` - 파란색 정보 박스
- `.warning-box` - 노란색 경고 박스
- `.code-box` - 점선 테두리 코드 박스
- `.code` - 코드 스타일 텍스트
- `.button` - 그라데이션 버튼

### 컨텍스트 변수

모든 템플릿에서 사용 가능:

- `{{ platform_name }}` - 플랫폼 이름
- `{{ settings }}` - Django settings 객체
- `{% now "Y" %}` - 현재 년도

---

## 📁 파일 구조

```
django-dashboard/
├── utils/
│   └── email.py                    # EmailUtils 클래스
├── templates/
│   └── emails/
│       ├── base.html              # 기본 레이아웃
│       ├── verification_code.html # 인증번호
│       ├── welcome.html           # 회원가입 환영
│       ├── password_reset.html    # 비밀번호 재설정
│       ├── password_changed.html  # 비밀번호 변경 알림
│       ├── account_deactivated.html # 계정 비활성화
│       └── login_notification.html  # 로그인 알림
├── test_email_utils.py            # 테스트 스크립트
└── test_platform_name.py          # 플랫폼 이름 테스트
```

---

## 🔒 보안 기능

- ✅ **인증번호 자동 만료**: 5분 후 자동 삭제
- ✅ **재설정 토큰 자동 만료**: 30분 후 자동 삭제
- ✅ **일회용 인증**: 검증 성공 시 자동 삭제
- ✅ **캐시 기반 저장**: 데이터베이스 부하 감소
- ✅ **로그인 알림**: IP, 디바이스 정보 포함

---

## 🎯 주요 특징

### 1. 플랫폼 이름 동적 처리

`.env` 파일의 `PLATFORM_NAME`만 변경하면 모든 이메일에 자동 적용

### 2. 년도 자동 렌더링

매년 수동으로 업데이트할 필요 없이 자동으로 현재 년도 표시

### 3. 캐시 기반 인증

빠른 검증과 자동 만료로 안전한 인증 시스템

### 4. 템플릿 재사용

`base.html`을 상속받아 일관된 디자인 유지

### 5. HTML/텍스트 병행 발송

이메일 클라이언트 호환성 극대화

---

## 💡 팁

### 환경별 설정

```env
# 개발 환경
PLATFORM_NAME=플랫폼 DEV

# 스테이징 환경
PLATFORM_NAME=플랫폼 STAGING

# 프로덕션 환경
PLATFORM_NAME=플랫폼이름
```

### 에러 로깅

`utils/email.py`에서:

```python
import logging
logger = logging.getLogger(__name__)

except Exception as e:
    logger.error(f"이메일 전송 실패: {type(e).__name__}: {str(e)}")
    return False
```

### 비동기 발송 (Celery)

```python
from celery import shared_task

@shared_task
def send_welcome_email_async(email, username, full_name):
    return EmailUtils.send_welcome_email(email, username, full_name)
```

---

**이메일 시스템이 완벽하게 작동합니다!** 🎉

문의사항이나 버그 리포트는 개발팀에 연락주세요.
