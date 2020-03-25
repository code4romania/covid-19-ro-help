from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import PaymentOrder, PaymentResponse


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    icon_name = "shopping_cart"
    list_display = ["order_id", "ngo", "first_name", "last_name", "amount"]
    search_fields = ["ngo__name"]
    list_filter = ["ngo", "date"]


@admin.register(PaymentResponse)
class PaymentResponseAdmin(admin.ModelAdmin):
    icon_name = "credit_card"
