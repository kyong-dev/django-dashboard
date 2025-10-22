# GitHub Copilot 설정 가이드

이 폴더에는 GitHub Copilot이 프로젝트의 코딩 스타일과 규칙을 이해하도록 돕는 인스트럭션 파일들이 있습니다.

## 📁 파일 구조

```
.github/
├── copilot-instructions.md      # 공통 Django 가이드라인 (자동 인식)
└── custom-instructions.md        # 프로젝트별 커스텀 규칙
```

## 🔧 설정 파일 설명

### 1. `copilot-instructions.md` (자동 인식)
- **목적**: Django 프로젝트 전반의 공통 가이드라인
- **내용**:
  - Django 모델 작성 규칙
  - API 응답/요청 camelCase 변환
  - Django Unfold Admin 작성 가이드
  - DRF Spectacular API 문서화
- **특징**: GitHub Copilot이 **자동으로 인식**하는 특수 파일

### 2. `custom-instructions.md` (프로젝트별)
- **목적**: 현재 프로젝트만의 특정 규칙
- **내용**:
  - 타입 힌트 사용 규칙
  - ViewSet/Admin 패턴
  - 이메일 시스템 사용법
  - 환경 변수 구조
  - 테스트 작성 패턴
  - Pre-commit Hooks 설정
- **특징**: 프로젝트별로 다르게 설정 가능

## 🚀 사용 방법

### 방법 1: 자동 인식 (copilot-instructions.md)
`.github/copilot-instructions.md` 파일은 별도 설정 없이 **자동으로 모든 Copilot 요청에 포함**됩니다.

### 방법 2: 채팅에서 파일 참조
VS Code Copilot Chat에서 특정 파일을 참조하려면:

1. **@workspace 사용**:
   ```
   @workspace custom-instructions.md 파일을 참고해서 ViewSet 만들어줘
   ```

2. **파일 직접 첨부**:
   - Copilot Chat 창에서 📎 (클립) 아이콘 클릭
   - `.github/custom-instructions.md` 선택
   - 질문 입력

3. **`#file` 사용**:
   ```
   #file:custom-instructions.md 의 타입 힌트 규칙을 따라서 코드 작성해줘
   ```

### 방법 3: VS Code 설정 활용
`.vscode/settings.json`에 다음 설정이 추가되어 있습니다:

```json
{
  "github.copilot.enable": {
    "*": true,
    "python": true,
    "markdown": true
  }
}
```

## 📝 인스트럭션 파일 작성 팁

### 1. 명확한 예제 코드 포함
```markdown
### ✅ 좋은 예
\`\`\`python
def create_user(self, username: str) -> User:
    pass
\`\`\`

### ❌ 나쁜 예
\`\`\`python
def create_user(self, username):
    pass
\`\`\`
```

### 2. 프로젝트별 컨벤션 명시
```markdown
## 네이밍 규칙
- 모델: PascalCase (User, UserProfile)
- 함수/변수: snake_case (get_user, user_list)
- 상수: UPPER_SNAKE_CASE (MAX_LENGTH, DEFAULT_TIMEOUT)
```

### 3. 자주 사용하는 패턴 정리
```markdown
## ViewSet 기본 패턴
\`\`\`python
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True)
\`\`\`
```

## 🔄 업데이트 방법

### 공통 가이드라인 업데이트
```bash
# copilot-instructions.md 수정
vim .github/copilot-instructions.md
```

### 프로젝트별 규칙 추가
```bash
# custom-instructions.md 수정
vim .github/custom-instructions.md
```

### 변경사항 적용
- 파일 저장 후 **VS Code 재시작** (권장)
- 또는 Copilot Chat 새 세션 시작

## 🎯 실제 사용 예시

### 예시 1: 타입 힌트가 적용된 모델 생성
**질문**:
```
@workspace User 모델과 유사한 Profile 모델 만들어줘
```

**결과**: 
- `copilot-instructions.md`의 Django 모델 가이드라인
- `custom-instructions.md`의 타입 힌트 규칙
이 자동으로 적용됨

### 예시 2: API ViewSet 생성
**질문**:
```
#file:custom-instructions.md ViewSet 패턴으로 ProfileViewSet 만들어줘
```

**결과**:
- 타입 힌트 포함
- DRF Spectacular 문서화 포함
- QuerySet 최적화 포함

### 예시 3: 이메일 전송 코드
**질문**:
```
사용자 등록 시 환영 이메일 보내는 코드 작성해줘
```

**결과**:
- `custom-instructions.md`의 EmailUtils 사용 예제가 자동 적용

## 📚 추가 리소스

### 프로젝트 문서
- [API 가이드](/docs/API_GUIDE.md)
- [이메일 가이드](/docs/EMAIL_GUIDE.md)
- [메인 README](/docs/README.md)

### Django 문서
- [Django Official](https://docs.djangoproject.com/)
- [DRF](https://www.django-rest-framework.org/)
- [DRF Spectacular](https://drf-spectacular.readthedocs.io/)

## ⚠️ 주의사항

1. **민감한 정보 제외**:
   - API 키, 비밀번호 등은 절대 인스트럭션 파일에 포함하지 마세요
   - 환경 변수 예시만 표시

2. **파일 크기**:
   - 너무 큰 파일은 Copilot이 전체를 인식하지 못할 수 있음
   - 각 파일을 1000줄 이하로 유지 권장

3. **업데이트 주기**:
   - 프로젝트 진행 중 규칙이 변경되면 즉시 업데이트
   - 팀원들과 공유

## 🤝 기여 방법

인스트럭션 개선 아이디어가 있다면:

1. `.github/custom-instructions.md` 수정
2. 커밋: `git commit -m "Update Copilot instructions: [변경 내용]"`
3. 팀원들과 공유

---

**마지막 업데이트**: 2025-10-22
**문의**: 개발팀
