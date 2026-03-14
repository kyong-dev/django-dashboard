from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

import environ

env = environ.Env(DEBUG=(bool, False))

MAIN_COLOR_CODE = env("MAIN_COLOR_CODE", default="000000")


def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


start_rgb = hex_to_rgb(MAIN_COLOR_CODE)
end_rgb = (255, 255, 255)
steps = [950, 900, 800, 700, 600, 500, 400, 300, 200, 100, 50, 0]


def generate_color_gradients(start_rgb, end_rgb, steps):
    color_dict = {}

    r_delta = (end_rgb[0] - start_rgb[0]) / (len(steps) - 1)
    g_delta = (end_rgb[1] - start_rgb[1]) / (len(steps) - 1)
    b_delta = (end_rgb[2] - start_rgb[2]) / (len(steps) - 1)

    for i, step in enumerate(steps):
        r = round(start_rgb[0] + r_delta * i)
        g = round(start_rgb[1] + g_delta * i)
        b = round(start_rgb[2] + b_delta * i)
        color_dict[str(step)] = f"{r} {g} {b}"

    return color_dict


color_dict = generate_color_gradients(start_rgb, end_rgb, steps)

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
    "ENVIRONMENT": "config.views.environment_callback",  # "Development", "Staging", "Production"
    "DASHBOARD_CALLBACK": "config.views.dashboard_callback",
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
        "primary": color_dict,
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
                    {
                        "title": _("관리자"),
                        "icon": "shield_person",  # Supported icon set: https://fonts.google.com/icons
                        "link": reverse_lazy("admin:user_adminuser_changelist"),
                        "permission": "config.views.superuser_permission_callback",
                    },
                    {
                        "title": _("사용자"),
                        "icon": "person",
                        "link": reverse_lazy("admin:user_user_changelist"),
                        "permission": "config.views.superuser_permission_callback",
                    },
                    {
                        "title": _("그룹"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": "config.views.superuser_permission_callback",
                    },
                    {
                        "title": _("로그"),
                        "icon": "history",
                        "link": reverse_lazy("admin:admin_logentry_changelist"),
                        "permission": "config.views.superuser_permission_callback",
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
                    # "permission": "config.views.admin_permission_callback",
                },
            ],
        },
    ],
}
