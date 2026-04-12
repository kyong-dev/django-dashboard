#!/bin/bash
# Commitizen commit message validator with detailed error guide

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

if cz check --commit-msg-file "$COMMIT_MSG_FILE" > /dev/null 2>&1; then
    exit 0
fi

# ── 실패 시 상세 안내 ──
echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  ❌  커밋 메시지 형식이 올바르지 않습니다"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "  입력한 메시지: \"$COMMIT_MSG\""
echo ""
echo "  ┌─────────────────────────────────────────────────────────┐"
echo "  │  올바른 형식: <type>(<scope>): <subject>                │"
echo "  └─────────────────────────────────────────────────────────┘"
echo ""
echo "  타입 목록:"
echo "  ─────────────────────────────────────────────────────────"
echo "    feat:      새 기능 추가                → minor (1.1.0)"
echo "    fix:       버그 수정                   → patch (1.0.1)"
echo "    docs:      문서 변경"
echo "    style:     코드 포맷팅 (기능 변경 없음)"
echo "    refactor:  리팩토링 (기능 변경 없음)"
echo "    perf:      성능 개선                   → patch (1.0.1)"
echo "    test:      테스트 추가/수정"
echo "    build:     빌드 시스템/의존성 변경"
echo "    ci:        CI 설정 변경"
echo "    chore:     기타 잡무"
echo ""
echo "  스코프 예시 (선택사항):"
echo "    migration, auth, api, admin, user, config ..."
echo ""
echo "  사용 예시:"
echo "  ─────────────────────────────────────────────────────────"
echo "    feat(migration): User 모델에 deactivated_at 필드 추가"
echo "    fix(auth): 로그인 세션 만료 버그 수정"
echo "    docs: API 가이드 업데이트"
echo "    chore: .gitignore 정리"
echo ""
echo "  💡 대화형 커밋 도우미: cz commit"
echo "══════════════════════════════════════════════════════════════"
echo ""

exit 1
