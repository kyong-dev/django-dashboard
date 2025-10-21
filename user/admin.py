import time
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from config.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "registered_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password"),
            },
        ),
    )
    list_display = ("username", "email", "is_staff", "registered_at")
    readonly_fields = ("registered_at",)
    search_fields = ("username", "email")
    list_editable = ("is_staff",)
    actions = ("make_staff",)

    def make_staff(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        time.sleep(5)
