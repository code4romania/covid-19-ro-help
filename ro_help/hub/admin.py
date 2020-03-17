from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from django.utils import timezone
from admin_auto_filters.filters import AutocompleteFilter

from .models import NGO, NGONeed, PersonalRequest, NGOHelper


class NGOFilter(AutocompleteFilter):
    title = "NGO"
    field_name = "ngo"


class ActiveNGONeedFilter(SimpleListFilter):
    title = _("active")
    parameter_name = "ngoneed__resolved_on"

    def lookups(self, request, model_admin):
        return [("active", "active"), ("resolved", "resolved")]

    def queryset(self, request, queryset):
        value = str(self.value()).lower() if self.value() else ""

        if value == "active":
            return queryset.active()

        if value == "resolved":
            return queryset.resolved()

        return queryset


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    icon_name = 'home_work'
    list_per_page = 25

    list_display = ("name", "email", "phone", "city", "county", "created")
    list_filter = (
        "city",
        "county",
    )
    search_fields = (
        "name",
        "email",
    )

    def get_queryset(self, request):
        user = request.user
        qs = super(NGOAdmin, self).get_queryset(request)
        if 'Admin' not in user.groups.values_list('name', flat=True):
            return qs.filter(users__in=[user])
        else:
            return qs

    def get_readonly_fields(self, request, obj=None):
        if obj:
            user = request.user
            if 'Admin' not in user.groups.values_list('name', flat=True):
                return ["users"]
        return []

class NGOHelperInline(admin.TabularInline):
    model = NGOHelper
    fields = ("name", "email", "message", "phone", "read")
    can_delete = False
    verbose_name_plural = _("Helpers")
    readonly_fields = ["name", "email", "message", "phone"]
    extra = 0

    # def get_readonly_fields(self, request, obj=None):
    #     # if obj:
    #         # if obj.factura.exists():
    #             # return self.get_fields(request, obj)
    #     return ["name", "email", "message", "phone"]



@admin.register(NGONeed)
class NGONeedAdmin(admin.ModelAdmin):
    icon_name = 'transfer_within_a_station'
    list_per_page = 25

    list_display = ("title", "ngo", "urgency", "kind", "created",
                    "responses", "new_responses", "resolved_on")
    list_filter = (NGOFilter, ActiveNGONeedFilter, "urgency",
                   "kind", "ngo__city", "ngo__county")
    readonly_fields = ["resolved_on"]
    inlines = [NGOHelperInline]
    actions = ["close_need"]
    search_fields = (
        "ngo__name",
        "ngo__email",
    )

    class Media:
        pass

    def get_queryset(self, request):
        user = request.user
        qs = super(NGONeedAdmin, self).get_queryset(request)
        if 'Admin' not in user.groups.values_list('name', flat=True):
            return qs.filter(ngo__users__in=[user])
        else:
            return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super(NGONeedAdmin, self).get_form(request, obj, **kwargs)
        user = request.user
        if 'Admin' not in user.groups.values_list('name', flat=True):
            ngos_pks = user.ngos.values_list('pk', flat=True)
            try:
                form.base_fields['ngo'].queryset = NGO.objects.filter(
                    pk__in=ngos_pks)
            except:
                pass
        return form

    def get_changeform_initial_data(self, request):
        user = request.user
        if user.ngos.count() == 1:
            return {'ngo': user.ngos.all()[0].pk}

    def responses(self, obj):
        if obj.helpers.exists():
            html = f"<span><a href='/admin/hub/ngoneed/{obj.pk}/change/'>{obj.helpers.count()}  </a></span>"
            return format_html(html)
        return 0

    responses.short_description = _("Responses")

    def new_responses(self, obj):
        if obj.helpers.filter(read=False).exists():
            html = f"<span><a href='/admin/hub/ngoneed/{obj.pk}/change/'>{obj.helpers.filter(read=False).count()}  </a></span>"
            return format_html(html)
        return 0

    new_responses.short_description = _("Unread")

    def close_need(self, request, queryset):
        closed = 0
        for need in queryset:
            need.resolved_on = timezone.now()
            need.save()
            closed += 1

        if closed == 1:
            user_msg = f"{closed} need closed"
        else:
            user_msg = f"{closed} needs closed"
        return self.message_user(request, user_msg, level=messages.INFO)

    close_need.short_description = _("Close need")

# @admin.register(NGOHelper)
# class NGOHelperAdmin(admin.ModelAdmin):
#     list_per_page = 25

#     list_display = ("need", "name", "email", "message", "phone", "read")
#     list_filter = ("read",)
#     search_fields = (
#         "ngo_need__title",
#         "name",
#         "email"
#     )

#     class Media:
#         pass

#     def get_queryset(self, request):
#         user = request.user
#         qs = super(NGOHelperAdmin, self).get_queryset(request)
#         if 'Admin' not in user.groups.values_list('name', flat=True):
#             return qs.filter(ngo_need__ngo__users__in=[user])
#         else:
#             return qs

#     def need(self, obj):
#         return obj.ngo_need.title


@admin.register(PersonalRequest)
class PersonalRequestAdmin(admin.ModelAdmin):
    pass
