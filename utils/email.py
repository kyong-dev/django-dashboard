"""
이메일 전송 유틸리티
다양한 이메일 템플릿을 관리하고 전송하는 클래스
"""

import random
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailUtils:
    """이메일 전송 유틸리티 클래스"""

    # 기본 설정
    DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    VERIFICATION_CODE_TIMEOUT = 300  # 5분
    PASSWORD_RESET_TIMEOUT = 1800  # 30분
    PLATFORM_NAME = getattr(settings, "PLATFORM_NAME", "플랫폼")

    @staticmethod
    def _get_base_context() -> Dict[str, Any]:
        """
        모든 이메일 템플릿에 공통으로 들어가는 컨텍스트

        Returns:
            dict: 기본 컨텍스트
        """
        return {
            "platform_name": EmailUtils.PLATFORM_NAME,
            "settings": settings,
        }

    @staticmethod
    def _send_email(subject: str, html_content: str, recipient_list: List[str], from_email: Optional[str] = None, text_content: Optional[str] = None) -> bool:
        """
        이메일 전송 기본 메서드

        Args:
            subject: 이메일 제목
            html_content: HTML 본문
            recipient_list: 수신자 리스트
            from_email: 발신자 (기본값: DEFAULT_FROM_EMAIL)
            text_content: 텍스트 본문 (기본값: HTML에서 태그 제거)

        Returns:
            bool: 전송 성공 여부
        """
        try:
            if from_email is None:
                from_email = EmailUtils.DEFAULT_FROM_EMAIL

            if text_content is None:
                text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return True

        except Exception as e:
            # 로깅 처리 (선택사항)
            print(f"이메일 전송 실패: {type(e).__name__}: {str(e)}")
            return False

    @staticmethod
    def send_verification_code(email: str, code: Optional[str] = None) -> Dict[str, Any]:
        """
        이메일 인증번호 발송

        Args:
            email: 수신자 이메일
            code: 인증번호 (None이면 자동 생성)

        Returns:
            dict: {'success': bool, 'code': str, 'message': str}
        """
        if code is None:
            code = str(random.randint(100000, 999999))

        # 캐시에 저장
        cache.set(f"email_verification:{email}", code, timeout=EmailUtils.VERIFICATION_CODE_TIMEOUT)

        # HTML 컨텍스트
        context = EmailUtils._get_base_context()
        context.update(
            {
                "code": code,
                "valid_minutes": EmailUtils.VERIFICATION_CODE_TIMEOUT // 60,
            }
        )

        html_content = render_to_string("emails/verification_code.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 이메일 인증번호 안내"

        success = EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

        return {"success": success, "code": code, "message": "인증번호가 발송되었습니다." if success else "이메일 발송에 실패했습니다."}

    @staticmethod
    def send_welcome_email(email: str, username: str, full_name: Optional[str] = None) -> bool:
        """
        회원가입 환영 이메일 발송

        Args:
            email: 수신자 이메일
            username: 사용자명
            full_name: 전체 이름 (선택)

        Returns:
            bool: 전송 성공 여부
        """
        context = EmailUtils._get_base_context()
        context.update(
            {
                "username": username,
                "full_name": full_name or username,
            }
        )

        html_content = render_to_string("emails/welcome.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 회원가입을 환영합니다!"

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def send_password_reset_email(email: str, reset_token: str, username: str) -> bool:
        """
        비밀번호 재설정 이메일 발송

        Args:
            email: 수신자 이메일
            reset_token: 비밀번호 재설정 토큰
            username: 사용자명

        Returns:
            bool: 전송 성공 여부
        """
        # 토큰을 캐시에 저장
        cache.set(f"password_reset:{email}", reset_token, timeout=EmailUtils.PASSWORD_RESET_TIMEOUT)

        # 재설정 링크 생성
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}&email={email}"

        context = EmailUtils._get_base_context()
        context.update(
            {
                "username": username,
                "reset_url": reset_url,
                "valid_minutes": EmailUtils.PASSWORD_RESET_TIMEOUT // 60,
            }
        )

        html_content = render_to_string("emails/password_reset.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 비밀번호 재설정 안내"

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def send_password_changed_notification(email: str, username: str) -> bool:
        """
        비밀번호 변경 완료 알림 이메일 발송

        Args:
            email: 수신자 이메일
            username: 사용자명

        Returns:
            bool: 전송 성공 여부
        """
        context = EmailUtils._get_base_context()
        context.update(
            {
                "username": username,
            }
        )

        html_content = render_to_string("emails/password_changed.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 비밀번호가 변경되었습니다"

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def send_account_deactivation_email(email: str, username: str) -> bool:
        """
        계정 비활성화 알림 이메일 발송

        Args:
            email: 수신자 이메일
            username: 사용자명

        Returns:
            bool: 전송 성공 여부
        """
        context = EmailUtils._get_base_context()
        context.update(
            {
                "username": username,
            }
        )

        html_content = render_to_string("emails/account_deactivated.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 계정이 비활성화되었습니다"

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def send_login_notification(email: str, username: str, ip_address: Optional[str] = None, device_info: Optional[str] = None) -> bool:
        """
        로그인 알림 이메일 발송 (보안)

        Args:
            email: 수신자 이메일
            username: 사용자명
            ip_address: 로그인 IP 주소
            device_info: 디바이스 정보

        Returns:
            bool: 전송 성공 여부
        """
        context = EmailUtils._get_base_context()
        context.update(
            {
                "username": username,
                "ip_address": ip_address or "알 수 없음",
                "device_info": device_info or "알 수 없음",
            }
        )

        html_content = render_to_string("emails/login_notification.html", context)
        subject = f"[{EmailUtils.PLATFORM_NAME}] 새로운 로그인이 감지되었습니다"

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def send_custom_email(email: str, subject: str, template_name: str, context: Dict[str, Any]) -> bool:
        """
        커스텀 템플릿으로 이메일 발송

        Args:
            email: 수신자 이메일
            subject: 이메일 제목
            template_name: 템플릿 파일명 (templates/emails/ 기준)
            context: 템플릿 컨텍스트

        Returns:
            bool: 전송 성공 여부
        """
        # 기본 컨텍스트와 병합
        full_context = EmailUtils._get_base_context()
        full_context.update(context)

        html_content = render_to_string(f"emails/{template_name}", full_context)

        return EmailUtils._send_email(subject=subject, html_content=html_content, recipient_list=[email])

    @staticmethod
    def verify_code(email: str, code: str) -> bool:
        """
        인증번호 검증

        Args:
            email: 이메일
            code: 입력받은 인증번호

        Returns:
            bool: 검증 성공 여부
        """
        cached_code = cache.get(f"email_verification:{email}")

        if cached_code and cached_code == code:
            # 검증 성공 시 캐시에서 삭제
            cache.delete(f"email_verification:{email}")
            return True

        return False

    @staticmethod
    def verify_password_reset_token(email: str, token: str) -> bool:
        """
        비밀번호 재설정 토큰 검증

        Args:
            email: 이메일
            token: 재설정 토큰

        Returns:
            bool: 검증 성공 여부
        """
        cached_token = cache.get(f"password_reset:{email}")

        if cached_token and cached_token == token:
            # 검증 성공 시 캐시에서 삭제
            cache.delete(f"password_reset:{email}")
            return True

        return False
