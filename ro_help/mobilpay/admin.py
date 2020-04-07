from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import PaymentOrder, PaymentResponse
from hub.models import (
    ADMIN_GROUP_NAME,
    NGO_GROUP_NAME,
    DSU_GROUP_NAME,
    FFC_GROUP_NAME,
)


class PaymentResponseInline(admin.TabularInline):
    model = PaymentResponse
    fields = ("date", "action", "error_code", "error_type", "error_message")
    readonly_fields = ("date",)
    can_delete = False
    can_add = False
    verbose_name_plural = _("Responses")
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    icon_name = "shopping_cart"
    list_display = ["order_id", "ngo", "first_name", "last_name", "amount"]
    search_fields = ["ngo__name"]
    list_filter = ["ngo", "date"]
    inlines = [PaymentResponseInline]


@admin.register(PaymentResponse)
class PaymentResponseAdmin(admin.ModelAdmin):
    icon_name = "credit_card"
    list_display = ["payment_order", "order_id", "date", "action", "error_code", "error_type", "error_message"]
    search_fields = ["payment_order__ngo__name"]
    list_filter = ["payment_order__ngo", "date", "action", "error_code"]


    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = request.user
        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
        if not user.groups.filter(name__in=authorized_groups).exists():
            return qs.filter(payment_order__ngo__users__pk__in=[user.ngos.values_list("pk", flat=True)])

        return qs

    def order_id(self, obj):
        try:
            return obj.payment_order.order_id
        except (PaymentOrder.DoesNotExist, AttributeError):
            return "-"
