from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter, helpers
from django.shortcuts import render
from django.contrib.auth.models import Group, User
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import activate
from django.db import models, transaction
from hub import utils
from .forms import RegisterNGORequestVoteForm, NGOForm
from .models import (
    NGO,
    KIND,
    NGOReportItem,
    NGONeed,
    NGOAccount,
    NGOHelper,
    ResourceTag,
    RegisterNGORequest,
    PendingRegisterNGORequest,
    RegisterNGORequestVote,
    ADMIN_GROUP_NAME,
    NGO_GROUP_NAME,
    DSU_GROUP_NAME,
    FFC_GROUP_NAME,
)


class NGOFilter(AutocompleteFilter):
    title = "NGO"
    field_name = "ngo"


class ActiveNGONeedFilter(SimpleListFilter):
    title = _("active")
    parameter_name = "ngoneed__resolved_on"

    def lookups(self, request, model_admin):
        return [("active", "active"), ("resolved", "resolved"), ("closed", "closed")]

    def queryset(self, request, queryset):
        value = str(self.value()).lower() if self.value() else ""

        if value == "active":
            return queryset.active()

        if value == "resolved":
            return queryset.resolved()

        if value == "closed":
            return queryset.closed()

        return queryset


class NGOAccountInline(admin.TabularInline):
    model = NGOAccount
    fields = ("currency", "bank", "iban")
    can_delete = True
    can_add = True
    verbose_name_plural = _("Bank Accounts")
    extra = 1


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    icon_name = "home_work"
    list_per_page = 25
    form = NGOForm

    list_display = ("name", "contact_name", "county", "city", "accepts_transfer", "accepts_mobilpay", "created")
    list_filter = (
        "city",
        "county",
    )
    search_fields = ("name", "email")
    inlines = [NGOAccountInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = request.user
        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            return qs.filter(users__in=[user])

        return qs

    def get_readonly_fields(self, request, obj=None):
        if not obj:
            return []

        user = request.user
        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            return ["users"]

        return []

    @transaction.atomic
    def save_model(self, request, ngo, form, change):
        super().save_model(request, ngo, form, change)
        if ngo.accepts_transfer:
            if not ngo.accounts.all():
                self.message_user(
                    request, _("To accept IBAN Transfers you need to add at least one account."), level=messages.ERROR,
                )
                ngo.accepts_transfer = False
                ngo.save()
        if ngo.accepts_transfer or ngo.accepts_mobilpay:
            NGONeed.objects.get_or_create(
                ngo=ngo,
                title=ngo.name,
                description=ngo.donations_description,
                kind=KIND.MONEY,
                city=ngo.city,
                county=ngo.county,
            )
        else:
            NGONeed.objects.filter(ngo=ngo, kind=KIND.MONEY).delete()


@admin.register(NGOReportItem)
class NGOReportItemAdmin(admin.ModelAdmin):
    icon_name = "receipt"
    list_per_page = 25

    list_display = ("date", "ngo", "title", "amount")
    list_filter = ("date",)
    search_fields = ("title", "ngo__name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = request.user
        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
        if not user.groups.filter(name__in=authorized_groups).exists():
            return qs.filter(ngo__pk__in=[user.ngos.values_list("pk", flat=True)])

        return qs

    def get_form(self, request, obj=None, **kwargs):
        user = request.user
        form = super().get_form(request, obj, **kwargs)

        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
        if not user.groups.filter(name__in=authorized_groups).exists():
            try:
                form.base_fields["ngo"].queryset = user.ngos
            except NGO.DoesNotExist:
                pass

        return form

    def get_changeform_initial_data(self, request):
        user = request.user
        if user.ngos.count() == 1:
            return {"ngo": user.ngos.first().pk}


class NGOHelperInline(admin.TabularInline):
    model = NGOHelper
    fields = ("name", "email", "message", "phone", "read")
    can_delete = False
    can_add = False
    verbose_name_plural = _("Helpers")
    readonly_fields = ["name", "email", "message", "phone"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NGONeed)
class NGONeedAdmin(admin.ModelAdmin):
    icon_name = "transfer_within_a_station"
    list_per_page = 25

    list_display = ("title", "ngo", "urgency", "kind", "created", "responses", "resolved_on", "closed_on")
    list_filter = (NGOFilter, ActiveNGONeedFilter, "urgency", "kind", "ngo__city", "ngo__county")
    readonly_fields = ["resolved_on", "closed_on"]
    inlines = [NGOHelperInline]
    actions = ["resolve_need", "close_need"]
    search_fields = (
        "title",
        "resource_tags__name",
        "kind",
        "ngo__name",
        "ngo__email",
    )

    class Media:
        pass

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("ngo").prefetch_related("helpers")

        user = request.user
        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            return qs.filter(ngo__users__in=[user])

        return qs

    def get_form(self, request, obj=None, **kwargs):
        user = request.user
        form = super().get_form(request, obj, **kwargs)

        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            try:
                form.base_fields["ngo"].queryset = user.ngos
                form.base_fields["kind"].choices = [(KIND.RESOURCE, KIND.RESOURCE), (KIND.VOLUNTEER, KIND.VOLUNTEER)]
            except NGO.DoesNotExist:
                pass
        return form

    def get_changeform_initial_data(self, request):
        user = request.user
        if user.ngos.count() == 1:
            return {"ngo": user.ngos.first().pk}

    def responses(self, obj):
        all_helpers = list(obj.helpers.all())
        new_helpers = [helper for helper in all_helpers if not helper.read]

        need_url = reverse("admin:hub_ngoneed_change", args=[obj.pk])

        if new_helpers:
            html = f"<span><a href='{need_url}'>{len(all_helpers)} ({len(new_helpers)} new)</a></span>"
        else:
            html = f"<span><a href='{need_url}'>{len(all_helpers)}</a></span>"

        return format_html(html)

    responses.short_description = _("Helpers")

    def resolve_need(self, request, queryset):
        queryset.update(resolved_on=timezone.now())

        user_msg = f"{queryset.count()} need{pluralize(queryset.count(), 's')} resolved"
        return self.message_user(request, user_msg, level=messages.INFO)

    resolve_need.short_description = _("Resolve need")

    def close_need(self, request, queryset):
        queryset.update(closed_on=timezone.now())

        user_msg = f"{queryset.count()} need{pluralize(queryset.count(), 's')} closed"
        return self.message_user(request, user_msg, level=messages.INFO)

    close_need.short_description = _("Close need")


@admin.register(ResourceTag)
class ResourceTagAdmin(admin.ModelAdmin):
    icon_name = "filter_vintage"
    search_fields = ("name",)


class RegisterNGORequestVoteInline(admin.TabularInline):
    model = RegisterNGORequestVote
    fields = ("entity", "vote", "motivation")
    can_delete = False
    can_add = False
    verbose_name_plural = _("Votes")
    readonly_fields = ["entity", "vote", "motivation"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RegisterNGORequest)
class RegisterNGORequestAdmin(admin.ModelAdmin):
    icon_name = "add_circle"
    fields = (
        "name",
        "description",
        "past_actions",
        "resource_types",
        "contact_name",
        "email",
        "contact_phone",
        "has_netopia_contract",
        "address",
        "city",
        "county",
        "social_link",
        "active",
        "resolved_on",
        "get_avatar",
        "avatar",
    )
    list_display = [
        "name",
        "county",
        "city",
        "voters",
        "yes",
        "no",
        "abstention",
        "active",
        "registered_on",
        "resolved_on",
        "get_last_balance_sheet",
        "get_statute",
    ]
    actions = ["create_account"]
    readonly_fields = ["active", "resolved_on", "registered_on", "get_avatar"]
    list_filter = ("city", "county", "registered_on")
    inlines = [RegisterNGORequestVoteInline]
    search_fields = ("name",)

    def get_changeform_initial_data(self, request):
        user = request.user
        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            return {"user": user.pk}

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not "Admin" in request.user.groups.values_list("name", flat=True):
            del actions["create_account"]
        return actions

    def get_last_balance_sheet(self, obj):
        if obj.last_balance_sheet:
            return format_html(f"<a class='' href='{obj.last_balance_sheet.url}'>{_('Open')}</a>")
        return "-"

    get_last_balance_sheet.short_description = _("Last balance")

    def get_statute(self, obj):
        if obj.statute:
            return format_html(f"<a class='' href='{obj.statute.url}'>{_('Open')}</a>")
        return "-"

    get_statute.short_description = _("Statute")

    def get_avatar(self, obj):
        if obj.avatar:
            return format_html(f"<img src='{obj.avatar.url}' width='200'>")
        return "-"

    get_avatar.short_description = _("Avatar Preview")

    def voters(self, obj):
        return ",".join(obj.votes.values_list("entity", flat=True))

    voters.short_description = _("Voters")

    def create_account(self, request, queryset):
        ngo_group = Group.objects.get(name=NGO_GROUP_NAME)

        for register_request in queryset:
            register_request.activate(request, ngo_group)

        user_msg = f"{queryset.count()} ngo{pluralize(queryset.count(), 's')} activated"
        return self.message_user(request, user_msg, level=messages.INFO)

    create_account.short_description = _("Create account")


@admin.register(PendingRegisterNGORequest)
class PendingRegisterNGORequestAdmin(admin.ModelAdmin):
    icon_name = "restore"
    list_display = ["name", "county", "city", "registered_on", "get_last_balance_sheet", "get_statute"]
    fields = (
        "name",
        "description",
        "past_actions",
        "resource_types",
        "contact_name",
        "email",
        "contact_phone",
        "has_netopia_contract",
        "address",
        "city",
        "county",
        "social_link",
        "active",
        "resolved_on",
        "get_avatar",
    )
    list_filter = ("city", "county", "registered_on")
    search_fields = ("name",)
    actions = ["vote"]
    inlines = [RegisterNGORequestVoteInline]

    def get_last_balance_sheet(self, obj):
        if obj.last_balance_sheet:
            return format_html(f"<a class='' href='{obj.last_balance_sheet.url}'>{_('Open')}</a>")
        return "-"

    get_last_balance_sheet.short_description = _("Last balance")

    def get_statute(self, obj):
        if obj.statute:
            return format_html(f"<a class='' href='{obj.statute.url}'>{_('Open')}</a>")
        return "-"

    get_statute.short_description = _("Statute")

    def get_avatar(self, obj):
        if obj.avatar:
            return format_html(f"<img src='{obj.avatar.url}' width='200'>")
        return "-"

    get_avatar.short_description = "Avatar"

    def vote(self, request, queryset):
        activate(request.LANGUAGE_CODE)
        if request.POST.get("post") == "yes":
            authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
            user = request.user
            base_path = f"{request.scheme}://{request.META['HTTP_HOST']}"
            user_groups = user.groups.values_list("name", flat=True)
            entity = list(set(authorized_groups).intersection(user_groups))[0]

            for ngo_request in queryset:
                vote = RegisterNGORequestVote.objects.create(
                    user=user,
                    ngo_request=ngo_request,
                    entity=entity,
                    vote=request.POST.get("vote"),
                    motivation=request.POST.get("motivation"),
                )

                notify_groups = list(set(authorized_groups) - set(user_groups))
                e = 0
                for group in Group.objects.filter(name__in=notify_groups):
                    for user in group.user_set.all():
                        e += utils.send_email(
                            template="mail/new_vote.html",
                            context={"vote": vote, "user": user, "base_path": base_path},
                            subject=f"[RO HELP] {entity} a votat pentru {ngo_request.name}",
                            to=user.email,
                        )
                self.message_user(
                    request,
                    _(
                        "Vote succesfully registered. {} email{} sent to others admins".format(
                            e, pluralize(e, str(_("s")))
                        )
                    ),
                    level=messages.INFO,
                )
        else:
            context = dict(
                title=f"Vot ONG",
                opts=self.model._meta,
                queryset=queryset,
                form=RegisterNGORequestVoteForm,
                action_checkbox_name=helpers.ACTION_CHECKBOX_NAME,
            )
            return render(request, "admin/vote_motivation.html", context)

    vote.short_description = _("Vote NGO")

    def get_queryset(self, request):
        user = request.user
        user_groups = user.groups.values_list("name", flat=True)
        return self.model.objects.exclude(votes__entity__in=user_groups)

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(RegisterNGORequestVote)
class RegisterNGORequestVoteAdmin(admin.ModelAdmin):
    icon_name = "how_to_vote"
    list_display = ["ngo_request", "user", "entity", "vote", "motivation", "date"]
    search_fields = ["ngo_request__name"]
    list_filter = ["user", "entity", "vote", "date"]

    def get_queryset(self, request):
        user = request.user

        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            user_groups = user.groups.values_list("name", flat=True)
            return self.model.objects.filter(entity__in=user_groups)

        return self.model.objects.all()

    def has_change_permission(self, request, obj=None):
        return False

    # def get_form(self, request, obj=None, **kwargs):
    #     user = request.user
    #     form = super().get_form(request, obj, **kwargs)

    #     if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
    #         form.base_fields["user"].queryset = User.objects.filter(pk=user.pk)

    #     return form

    def get_changeform_initial_data(self, request):
        user = request.user
        if not user.groups.filter(name=ADMIN_GROUP_NAME).exists():
            return {"user": user.pk}
