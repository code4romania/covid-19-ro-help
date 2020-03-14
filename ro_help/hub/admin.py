from django.contrib import admin

from .models import NGO, NGONeed, PersonalRequest


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "city", "county", )
    list_filter = ("city", "county",)
    search_fields = ("name", "email", )


@admin.register(NGONeed)
class NGONeedAdmin(admin.ModelAdmin):
    list_display = ("ngo", "urgency", "kind",)
    list_filter = ("ngo", "urgency", "kind", "ngo__city", "ngo__county",)
    search_fields = ("ngo__name", "ngo__email", )


@admin.register(PersonalRequest)
class PersonalRequestAdmin(admin.ModelAdmin):
    pass
