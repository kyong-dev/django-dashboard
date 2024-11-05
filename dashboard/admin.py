from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin


admin.site.site_header = "대시보드"
admin.site.site_title = "대시보드"
admin.site.index_title = "대시보드"


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    filter_horizontal = ("permissions",)

    fieldsets = (
        (None, {"fields": ("name",)}),
        (_("Permissions"), {"fields": ("permissions",)}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("permissions")


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ("name", "codename", "content_type")
    search_fields = ("name", "codename")
    list_filter = ("content_type",)

    fieldsets = ((None, {"fields": ("name", "codename", "content_type")}),)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("content_type")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_or_change_permission(self, request, obj=None):
        return True


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ("action_time", "user", "content_type", "object_link", "action_flag", "change_message")
    list_filter = ("user", "content_type", "action_flag")
    search_fields = ("object_repr", "change_message")
    readonly_fields = ("action_time", "user", "content_type", "object_id", "object_repr", "action_flag", "change_message")

    def object_link(self, obj):
        if obj.action_flag == ADDITION:
            return format_html('<a href="{}">{}</a>', reverse("admin:%s_%s_change" % (obj.content_type.app_label, obj.content_type.model), args=[obj.object_id]), obj.object_repr)
        elif obj.action_flag == CHANGE:
            return format_html('<a href="{}">{}</a>', reverse("admin:%s_%s_change" % (obj.content_type.app_label, obj.content_type.model), args=[obj.object_id]), obj.object_repr)
        elif obj.action_flag == DELETION:
            return format_html("<span>{}</span>", obj.object_repr)
        return obj.object_repr

    object_link.allow_tags = True
    object_link.short_description = _("객체")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_or_change_permission(self, request, obj=None):
        return True
