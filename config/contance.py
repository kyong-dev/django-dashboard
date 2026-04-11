from django.utils.translation import gettext_lazy as _

from unfold.contrib.constance.settings import UNFOLD_CONSTANCE_ADDITIONAL_FIELDS

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_ADDITIONAL_FIELDS = {
    **UNFOLD_CONSTANCE_ADDITIONAL_FIELDS,
    "language_select": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
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
    "choice_field": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                ("light-blue", "Light blue"),
                ("dark-blue", "Dark blue"),
            ),
        },
    ],
    "currency_select": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "unfold.widgets.UnfoldAdminSelectWidget",
            "choices": (
                ("KRW", "KRW (\uc6d0)"),
                ("USD", "USD ($)"),
                ("EUR", "EUR (\u20ac)"),
                ("GBP", "GBP (\u00a3)"),
                ("JPY", "JPY (\u00a5)"),
                ("CNY", "CNY (\u00a5)"),
                ("AUD", "AUD ($)"),
                ("CAD", "CAD ($)"),
            ),
        },
    ],
}

CONSTANCE_CONFIG = {
    # 사이트 기본 설정
    "SITE_NAME": ("My Platform", _("사이트 이름"), str),
    "SITE_DESCRIPTION": ("", _("사이트 설명"), str),
    "API_VERSION": ("1.0.0", _("API 버전 (예: 1.0.0)"), str),
    "DEFAULT_LANGUAGE": ("ko", _("기본 언어"), "language_select"),
    "MAINTENANCE_MODE": (False, _("점검 모드 활성화"), bool),
    # 사용자 설정
    "MAX_LOGIN_ATTEMPTS": (5, _("최대 로그인 시도 횟수"), int),
    "SESSION_TIMEOUT_MINUTES": (3600, _("세션 타임아웃 (분)"), int),
    "ALLOW_REGISTRATION": (True, _("회원가입 허용"), bool),
    # 화폐 설정
    "DEFAULT_CURRENCY": ("KRW", _("기본 화폐"), "currency_select"),
    # 이메일 설정
    "WELCOME_EMAIL_ENABLED": (True, _("가입 환영 이메일 발송"), bool),
    "SUPPORT_EMAIL": ("support@example.com", _("고객지원 이메일"), str),
}

CONSTANCE_CONFIG_FIELDSETS = (
    (
        _("사이트 설정"),
        {
            "fields": ("SITE_NAME", "SITE_DESCRIPTION", "API_VERSION", "DEFAULT_LANGUAGE", "MAINTENANCE_MODE"),
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
    (
        _("화폐 설정"),
        {
            "fields": ("DEFAULT_CURRENCY",),
            "collapse": False,
        },
    ),
    (
        _("이메일 설정"),
        {
            "fields": ("WELCOME_EMAIL_ENABLED", "SUPPORT_EMAIL"),
            "collapse": True,
        },
    ),
)
