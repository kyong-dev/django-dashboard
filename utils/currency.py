from constance import config  # type: ignore[import-untyped]


def get_default_currency():
    """Constance에서 설정된 기본 화폐 코드를 반환합니다."""
    return config.DEFAULT_CURRENCY
