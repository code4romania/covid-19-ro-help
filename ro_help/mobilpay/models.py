import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from hub.models import NGO


class PaymentOrder(TimeStampedModel):
    ngo = models.ForeignKey(
        NGO, related_name="payment_orders", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("NGO")
    )

    order_id = models.CharField(
        _("Order ID"), max_length=100, blank=True, unique=True, default=uuid.uuid4, editable=False
    )
    first_name = models.CharField(_("First name"), max_length=254)
    last_name = models.CharField(_("Last name"), max_length=254)
    show_name = models.BooleanField(
        default=False, verbose_name="Sunt de acord ca numele meu să apară pe platforma RoHelp"
    )
    phone = models.CharField(_("Phone"), max_length=30)
    email = models.EmailField(_("Email"),)
    address = models.CharField(_("Address"), max_length=254)
    details = models.TextField(_("Details"))
    amount = models.FloatField(_("Amount"))
    date = models.DateTimeField(_("Registered on"), auto_now_add=True)
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.amount}"

    class Meta:
        verbose_name_plural = _("Payment Orders")
        verbose_name = _("Payment Order")

    def is_pending(self):
        confirmed_pending = self.responses.filter(action="confirmed_pending").exists()
        paid_pending = self.responses.filter(action="paid_pending").exists()
        canceled = self.responses.filter(action="canceled").exists()
        return (confirmed_pending or paid_pending) and not canceled


class PaymentResponse(TimeStampedModel):
    payment_order = models.ForeignKey(
        PaymentOrder, null=True, blank=True, related_name="responses", on_delete=models.SET_NULL
    )
    action = models.CharField(max_length=100, null=True, blank=True)
    error_code = models.CharField(max_length=255, null=True, blank=True)
    error_type = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(_("Registered on"), auto_now_add=True)

    def __str__(self):
        return f"{self.payment_order} {self.error_code} {self.error_type} {self.error_message}"

    class Meta:
        verbose_name_plural = _("Payment responses")
        verbose_name = _("Payment response")
