from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from admin_auto_filters.filters import AutocompleteFilter

from .models import NGO, NGONeed, PersonalRequest


class NGOFilter(AutocompleteFilter):
    title = 'NGO'
    field_name = 'ngo'


class ActiveNGONeedFilter(SimpleListFilter):
    title = _('active')
    parameter_name = 'ngoneed__resolved_on'

    def lookups(self, request, model_admin):
        return [
            ("active", "active"),
            ("resolved", "resolved")
        ]

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
    list_filter = ("city", "county",)
    search_fields = ("name", "email", )


@admin.register(NGONeed)
class NGONeedAdmin(admin.ModelAdmin):
    list_per_page = 25

    list_display = ("ngo", "urgency", "kind", "created", "resolved_on")
    list_filter = (NGOFilter, ActiveNGONeedFilter, "urgency", "kind", "ngo__city", "ngo__county")
    search_fields = ("ngo__name", "ngo__email", )

    class Media:
        pass


@admin.register(PersonalRequest)
class PersonalRequestAdmin(admin.ModelAdmin):
    pass
