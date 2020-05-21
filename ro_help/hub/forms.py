from django import forms
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django_crispy_bulma.widgets import EmailInput

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from hub import models


class NGOHelperForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"required_score": 0.3, "action": "help"}), label="")

    class Meta:
        model = models.NGOHelper
        fields = ("name", "email", "message", "phone")
        widgets = {"email": EmailInput()}


class NGOForm(forms.ModelForm):
    class Meta:
        model = models.NGO
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        accepts_mobilpay = cleaned_data.get("accepts_mobilpay")
        accepts_transfer = cleaned_data.get("accepts_transfer")
        donations_description = cleaned_data.get("donations_description")
        mobilpay_icc = cleaned_data.get("mobilpay_icc")
        mobilpay_public_key = cleaned_data.get("mobilpay_public_key")
        mobilpay_private_key = cleaned_data.get("mobilpay_private_key")
        cif = cleaned_data.get("cif")
        cui = cleaned_data.get("cui")

        if accepts_mobilpay:
            if not donations_description:
                self.add_error("donations_description", _("To accept mobilpay donations this field is required."))
            if not mobilpay_icc:
                self.add_error("mobilpay_icc", _("To accept mobilpay donations this field is required."))
            if not mobilpay_public_key:
                self.add_error("mobilpay_public_key", _("To accept mobilpay donations this field is required."))
            if not mobilpay_private_key:
                self.add_error("mobilpay_private_key", _("To accept mobilpay donations this field is required."))
        if accepts_transfer:
            if not donations_description:
                self.add_error("donations_description", _("To accept money transfer this field is required"))
            if not cui:
                self.add_error("cui", _("To accept money transfer this field is required"))


class NGORegisterRequestForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"required_score": 0.3, "action": "register"}), label="")

    class Meta:
        model = models.RegisterNGORequest
        fields = [
            "name",
            "county",
            "city",
            "address",
            "email",
            "contact_name",
            "contact_phone",
            "social_link",
            "description",
            "past_actions",
            "resource_types",
            "has_netopia_contract",
            "avatar",
            "last_balance_sheet",
            "statute",
        ]
        widgets = {
            "email": EmailInput(),
            "city": forms.Select(
                attrs={
                    "class": "cityAutoComplete", 
                    "disabled": "true", 
                    "data-url": reverse_lazy("city-autocomplete")
                }
            ),
            # # "has_netopia_contract": forms.CheckboxInput(),
            # "avatar": AdminResubmitImageWidget,
            # "last_balance_sheet": AdminResubmitFileWidget,
            # "statute": AdminResubmitFileWidget,
        }


class RegisterNGORequestVoteForm(forms.ModelForm):
    class Meta:
        model = models.RegisterNGORequestVote
        fields = ("vote", "motivation")


class ImportCitiesForm(forms.Form):
    csv_file = forms.FileField(label=_("CSV file"))

    def clean_csv_file(self):
        f = self.cleaned_data["csv_file"]
        if not f.name.lower().endswith(".csv"):
            raise ValidationError(_("Uploaded file is not a CSV file"))
