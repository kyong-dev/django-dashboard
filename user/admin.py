import time
from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from config.admin import ModelAdmin

from .forms import UserForm
from .models import AdminUser, User


class AllUserAdmin(ModelAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email",)}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "registered_at")}),
        (
            _("Deactivation"),
            {"fields": ("deactivated_at",)},
        ),
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
    list_display = ("username", "email", "is_staff", "registered_at", "deactivated_at")
    readonly_fields = ("registered_at", "deactivated_at")
    search_fields = ("username", "email")
    list_editable = ("is_staff",)
    actions = ("make_staff",)
    form = UserForm

    def make_staff(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        time.sleep(5)


@admin.register(User)
class UserAdmin(AllUserAdmin):

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        return super().get_queryset(request).filter(is_staff=False)


@admin.register(AdminUser)
class AdminUserAdmin(AllUserAdmin):

    def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
        return super().get_queryset(request).filter(is_staff=True)
