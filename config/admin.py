import json

from django.contrib import admin
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin as UnfoldModelAdmin

admin.site.site_header = "대시보드"
admin.site.site_title = "대시보드"
admin.site.index_title = "대시보드"


admin.site.unregister(Group)


class ModelAdmin(UnfoldModelAdmin):
    def getLogMessage(self, form, add=False, formsetObj=None):
        """
        Return a list of messages describing the changes from the form.
        """
        changed_data = {} if form is None else form.changed_data
        data = {}
        change_message = []

        if formsetObj is not None:
            data = {
                "name": str(formsetObj._meta.verbose_name_plural),
                "object": f"{str(formsetObj)}({formsetObj.pk})",
            }
        if add:
            change_message.append({"added": data})
        elif form.changed_data:

            message = []
            for field in changed_data:
                initial = form.initial[field]
                cleaned_data = form.cleaned_data[field]

                message.append(f"""[{form.fields[field].label}] "{str(initial)}" => "{str(cleaned_data)}" """)
            data["fields"] = message
            change_message.append({"changed": data})
        return change_message

    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing changes from a changed
        """
        change_message = self.getLogMessage(form, add)

        if formsets:
            for formset in formsets:
                formList = {}

                pkName = ""
                if formset.__len__() > 0:
                    pkName = formset.forms[0]._meta.model._meta.pk.name

                for singleform in formset.forms:
                    try:
                        obj = singleform.cleaned_data[pkName]

                        if obj is None:
                            obj = singleform.initial.get(pkName)

                        if obj is not None:
                            formList[getattr(obj, pkName)] = singleform
                    except Exception as e:
                        print(e)

                for added_object in formset.new_objects:
                    message = self.getLogMessage(None, True, formsetObj=added_object)
                    change_message += message

                for changed_object, changed_fields in formset.changed_objects:
                    singleForm = formList[changed_object.pk]
                    message = self.getLogMessage(singleForm, False, formsetObj=changed_object)
                    change_message += message

                    self.log_change(request, changed_object, self.getLogMessage(singleForm, False))

                for deleted_object in formset.deleted_objects:
                    change_message.append(
                        {
                            "deleted": {
                                "name": str(deleted_object._meta.verbose_name_plural),
                                "object": str(deleted_object),
                            }
                        }
                    )
        return change_message


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


def parse_action_string(action_string, action_flag):
    try:
        if action_flag == 1:
            return "오브젝트가 추가되었습니다."
        if action_flag == 3:
            return "오브젝트가 삭제되었습니다."

        data = json.loads(action_string)
        results = []

        for entry in data:
            if "added" in entry and "name" in entry["added"]:
                object = entry["added"]["object"]
                results.append(f"'{object}'를 추가하였습니다.")

            elif "deleted" in entry and "name" in entry["deleted"]:
                object = entry["deleted"]["object"]
                results.append(f"'{object}'를 삭제하였습니다.")

            elif "changed" in entry and "fields" in entry["changed"]:
                for change in entry["changed"]["fields"]:
                    if "[" not in change:
                        results.append(f"'{change}' 필드를 변경하였습니다.")
                    else:
                        field_name = change.split("[")[1].split("]")[0]
                        old_value, new_value = change.split("=>")
                        old_value = old_value.split('"')[-2]
                        new_value = new_value.split('"')[-2]
                        if field_name == "비밀번호":
                            results.append(f"'{field_name}' 필드를 변경하였습니다.")
                        else:
                            results.append(f"'{field_name}' 필드의 '{old_value}'에서 '{new_value}'로 변경하였습니다.")
        return "\n".join(results)

    except json.JSONDecodeError:
        return "유효하지 않은 JSON 형식입니다."
    except Exception as e:
        return action_string


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ["action_time_str", "username", "object_repr_str", "action_flag_str", "change_message_str"]
    list_filter = ["action_time", "action_flag"]
    search_fields = ["object_repr", "user__username"]
    change_list_template = "admin/log/logentry_changelist.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description=_("시간"))
    def action_time_str(self, obj):
        return obj.action_time.strftime("%Y-%m-%d %H:%M")

    @admin.display(description=_("관리자"))
    def username(self, obj):
        return obj.user.username

    @admin.display(description=_("액션"))
    def action_flag_str(self, obj):
        if obj.action_flag == 1:
            return "추가"
        elif obj.action_flag == 2:
            return "변경"
        elif obj.action_flag == 3:
            return "삭제"
        return "-"

    @admin.display(description=_("수정대상"))
    def object_repr_str(self, obj):
        return format_html('<a style="color: blue;" href="{0}">{1}</a>', obj.get_admin_url(), obj.object_repr[:30] + "...")

    @admin.display(description=_("수정내용"))
    def change_message_str(self, obj):
        field_change = f"{obj.user.username}님이 {obj.content_type.app_label}탭의 ID: {obj.object_id}의 "
        field_change += parse_action_string(obj.change_message, obj.action_flag)
        return field_change
