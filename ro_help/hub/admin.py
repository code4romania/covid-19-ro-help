from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html

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

@admin.register(NGONeed)
class NGONeedAdmin(admin.ModelAdmin):
    list_per_page = 25

    list_display = ("title", "ngo", "urgency", "kind", "created", "responses", "new_responses", "resolved_on")
    list_filter = (NGOFilter, ActiveNGONeedFilter, "urgency", "kind", "ngo__city", "ngo__county")
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

    def responses(self, obj):
        if obj.helpers.exists():
            html = f"<span><a href='/admin/hub/ngohelper/?ngo_need__id__exact={obj.pk}' target='_blank'>{obj.helpers.count()}  </a></span>"
            return format_html(html)
        return 0

    responses.short_description = _("Responses")

    def new_responses(self, obj):
        if obj.helpers.filter(read=False).exists():
            html = f"<span><a href='/admin/hub/ngohelper/?ngo_need__id__exact={obj.pk}&read__exact=0' target='_blank'>{obj.helpers.filter(read=False).count()}  </a></span>"
            return format_html(html)
        return 0

    new_responses.short_description = _("Unread responses")


@admin.register(NGOHelper)
class NGOHelperAdmin(admin.ModelAdmin):
    list_per_page = 25

    list_display = ("need", "name", "email", "message", "phone", "read")
    list_filter = ("read",)
    search_fields = (
        "ngo_need__title",
        "name",
        "email"
    )

    class Media:
        pass

    def get_queryset(self, request):
        user = request.user
        qs = super(NGOHelperAdmin, self).get_queryset(request)
        if 'Admin' not in user.groups.values_list('name', flat=True):
            return qs.filter(ngo_need__ngo__users__in=[user])
        else:
            return qs

    def need(self, obj):
        return obj.ngo_need.title


@admin.register(PersonalRequest)
class PersonalRequestAdmin(admin.ModelAdmin):
    pass
