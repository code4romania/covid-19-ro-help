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


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    icon_name = "shopping_cart"
    list_display = ["order_id", "ngo", "first_name", "last_name", "amount"]
    search_fields = ["ngo__name"]
    list_filter = ["ngo", "date"]


@admin.register(PaymentResponse)
class PaymentResponseAdmin(admin.ModelAdmin):
    icon_name = "credit_card"


    def get_queryset(self, request):
        qs = super().get_queryset(request)

        user = request.user
        authorized_groups = [ADMIN_GROUP_NAME, DSU_GROUP_NAME, FFC_GROUP_NAME]
        if not user.groups.filter(name__in=authorized_groups).exists():
            return qs.filter(payment_order__ngo__users__pk__in=[user.ngos.values_list("pk", flat=True)])

        return qs
