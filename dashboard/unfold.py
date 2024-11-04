from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

unfold_settings = {
    "SITE_TITLE": "대시보드",
    "SITE_HEADER": "대시보드",
    "SITE_URL": "/",
    # "SITE_ICON": lambda request: static("icon.svg"),  # both modes, optimise for 32px height
    # "SITE_ICON": {
    #     "light": lambda request: static("icon-light.svg"),  # light mode
    #     "dark": lambda request: static("icon-dark.svg"),  # dark mode
    # },
    # "SITE_LOGO": lambda request: static("logo.svg"),  # both modes, optimise for 32px height
    # "SITE_LOGO": {
    #     "light": lambda request: static("logo-light.svg"),  # light mode
    #     "dark": lambda request: static("logo-dark.svg"),  # dark mode
    # },
    "SITE_SYMBOL": "settings",  # symbol from icon set
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.svg"),
        },
    ],
    "SHOW_HISTORY": True,  # show/hide "History" button, default: True
    "SHOW_VIEW_ON_SITE": True,  # show/hide "View on site" button, default: True
    "ENVIRONMENT": "dashboard.views.environment_callback",  # "Development", "Staging", "Production"
    "DASHBOARD_CALLBACK": "dashboard.views.dashboard_callback",
    # "THEME": "dark", # Force theme: "dark" or "light". Will disable theme switcher
    "LOGIN": {
        # "image": lambda request: static("sample/login-bg.jpg"),
        # "redirect_after": lambda request: reverse_lazy("admin:APP_MODEL_changelist"),
    },
    "STYLES": [
        lambda request: static("css/style.css"),
    ],
    "SCRIPTS": [
        lambda request: static("js/script.js"),
    ],
    "COLORS": {
        "primary": {
            "50": "240 245 255",
            "100": "230 235 255",
            "200": "210 220 255",
            "300": "180 200 255",
            "400": "140 170 255",
            "500": "100 140 255",
            "600": "70 110 255",
            "700": "50 90 255",
            "800": "30 70 255",
            "900": "20 50 255",
            "950": "10 30 255",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,  # Search in applications and models names
        "show_all_applications": False,  # Dropdown with all applications and models
        "navigation": [
            {
                "title": _("사용자 관리"),
                "separator": True,
                "collapsible": True,
                "items": [
                    # {
                    #     "title": _("관리자"),
                    #     "icon": "shield_person",  # Supported icon set: https://fonts.google.com/icons
                    #     "link": reverse_lazy("admin:users_admin_changelist"),
                    #     "permission": "newproject.views.admin_permission_callback",
                    # },
                    {
                        "title": _("사용자"),
                        "icon": "person",
                        "link": reverse_lazy("admin:user_user_changelist"),
                        # "badge": "dashboard.views.user_badge_callback",
                    },
                    {
                        "title": _("그룹"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": _("로그"),
                        "icon": "history",
                        "link": reverse_lazy("admin:admin_logentry_changelist"),
                        # "permission": "sodam.views.admin_permission_callback",
                    },
                ],
            },
            #         "title": _("Navigation"),
            #         "separator": True,  # Top border
            #         "collapsible": True,  # Collapsible group of links
            #         "items": [
            #             {
            #                 "title": _("Dashboard"),
            # #                 "icon": "dashboard",  # Supported icon set: https://fonts.google.com/icons
            #                 "link": reverse_lazy("admin:index"),
            # #                 # "badge": "sample_app.badge_callback",
            # #                 # "permission": lambda request: request.user.is_superuser,
            #             },
            # #             {
            # #                 "title": _("Users"),
            # #                 "icon": "people",
            # #                 # "link": reverse_lazy("admin:users_user_changelist"),
            # #             },
            #         ],
        ],
    },
    "TABS": [
        {
            "models": [
                "auth.group",
                "auth.permission",
            ],
            "items": [
                {
                    "title": _("그룹"),
                    "icon": "group",
                    "link": reverse_lazy("admin:auth_group_changelist"),
                },
                {
                    "title": _("허가"),
                    "icon": "lock",
                    "link": reverse_lazy("admin:auth_permission_changelist"),
                    # "permission": "sodam.views.admin_permission_callback",
                },
            ],
        },
    ],
}
