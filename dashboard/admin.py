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

class ModelAdmin(ModelAdmin):
    def getLogMessage(self, form, add=False, formsetObj=None):
        """
        Return a list of messages describing the changes from the form.
        """
        changed_data = {} if form is None else form.changed_data
        data = {}
        change_message = []

        if formsetObj is not None:
            data = {'name': str(formsetObj._meta.verbose_name_plural),
                    'object': f"{str(formsetObj)}({formsetObj.pk})", }
        if add:
            change_message.append({'added': data})
        elif form.changed_data:
            
            message = []
            for field in changed_data:
                initial = form.initial[field]
                cleaned_data = form.cleaned_data[field]
                
                message.append(
                    f"""[{form.fields[field].label}] "{str(initial)}" => "{str(cleaned_data)}" """)
            data['fields'] = message
            change_message.append({'changed': data})
        return change_message
	
    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing changes from a changed
        """
        change_message = self.getLogMessage(form, add)

        if formsets:
            for formset in formsets:
                formList = {}
                
                pkName = ''
                if formset.__len__() > 0:
                    pkName = formset.forms[0]._meta.model._meta.pk.name
                    
                for singleform in formset.forms:
                    try:
                        obj = singleform.cleaned_data[pkName]
                        
                        if(obj is None):
                            obj = singleform.initial.get(pkName)
                            
                        if(obj is not None):
                            formList[getattr(obj, pkName)] = singleform
                    except Exception as e:
                        print(e)

                for added_object in formset.new_objects:
                    message = self.getLogMessage(
                        None, True, formsetObj=added_object)
                    change_message += message
        
                for changed_object, changed_fields in formset.changed_objects:
                    singleForm = formList[changed_object.pk]
                    message = self.getLogMessage(
                        singleForm, False, formsetObj=changed_object)
                    change_message += message
                    
                    self.log_change(request, changed_object,
                                    self.getLogMessage(singleForm, False))
                                    
                for deleted_object in formset.deleted_objects:
                    change_message.append({
                        'deleted': {
                            'name': str(deleted_object._meta.verbose_name_plural),
                            'object': str(deleted_object),
                        }
                    })
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
