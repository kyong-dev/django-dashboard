# 📚 Django Dashboard 문서

프로젝트의 모든 문서가 정리되어 있습니다.

## 📑 문서 목록

### 🚀 [API 문서화 가이드](./API_GUIDE.md)

- API 문서화 시스템 사용법
- 태그 기반 분류 시스템
- ViewSet 및 APIView 문서화 방법
- Swagger UI 접근 URL

**주요 내용:**

- `/swagger/` - 전체 API 문서
- `/swagger/app/` - 앱 API 문서
- `/swagger/admin/` - 관리자 API 문서
- `/swagger/external/` - 외부 연동 API 문서

---

### 📧 [이메일 시스템 가이드](./EMAIL_GUIDE.md)

- 이메일 전송 유틸리티 사용법
- 7가지 이메일 템플릿
- Django View 통합 방법
- 플랫폼 이름 동적 설정

**주요 기능:**

- 🔢 이메일 인증번호 (5분 유효)
- 👋 회원가입 환영
- 🔐 비밀번호 재설정 (30분 유효)
- ✅ 비밀번호 변경 알림
- 😢 계정 비활성화 알림
- 🔔 로그인 보안 알림
- 🎨 커스텀 템플릿

---

## 🚀 빠른 시작

### API 문서 확인

```bash
# 개발 서버 실행
python manage.py runserver

# 브라우저에서
http://localhost:8000/swagger/
```

### 이메일 테스트

```bash
# 가상환경 활성화
source venv/bin/activate

# 테스트 실행
python test_email_utils.py
```

---

## 🔧 설정

### `.env` 파일 필수 설정

```env
# 플랫폼 이름
PLATFORM_NAME=나인위닛

# 이메일 SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com

# 프론트엔드 URL
FRONTEND_URL=http://localhost:3000
```

---

## 📁 프로젝트 구조

```
django-dashboard/
├── docs/
│   ├── README.md           # 📚 이 문서
│   ├── API_GUIDE.md        # 🚀 API 문서화 가이드
│   └── EMAIL_GUIDE.md      # 📧 이메일 시스템 가이드
├── config/
│   ├── schema_views/       # API 스키마 뷰
│   ├── settings.py
│   └── urls.py
├── utils/
│   └── email.py           # EmailUtils 클래스
├── templates/
│   └── emails/            # 이메일 템플릿들
├── user/
│   ├── views/             # API ViewSet들
│   └── urls/              # URL 패턴
└── test_email_utils.py    # 이메일 테스트
```

---

## 🆘 도움말

### 문제 해결

**API 문서가 보이지 않는다면:**

- `/swagger/` URL 접근 확인
- `INSTALLED_APPS`에 `drf_spectacular` 포함 확인

**이메일이 발송되지 않는다면:**

- `.env` 파일의 SMTP 설정 확인
- Gmail 앱 비밀번호 생성 확인
- `EMAIL_USE_TLS` 설정 확인

### 추가 문의

개발팀에 문의하세요.

---

**Last Updated:** 2025-10-03
