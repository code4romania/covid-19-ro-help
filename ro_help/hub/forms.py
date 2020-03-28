from django import forms
from django_crispy_bulma.widgets import EmailInput, FileUploadInput
from file_resubmit.admin import AdminResubmitFileWidget, AdminResubmitImageWidget

from hub import models
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class NGOHelperForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"required_score": 0.85,}), label="")

    class Meta:
        model = models.NGOHelper
        fields = ("name", "email", "message", "phone")
        widgets = {"email": EmailInput()}


class NGOForm(forms.ModelForm):
    class Meta:
        model = models.NGO
        fields = ("__all__")

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
                self.add_error('donations_description', "Pentru a accepta donatii prin mobilpay acest camp este obligatoriu")
            if not mobilpay_icc:
                self.add_error('mobilpay_icc', "Pentru a accepta donatii prin mobilpay acest camp este obligatoriu")
            if not mobilpay_public_key:
                self.add_error('mobilpay_public_key', "Pentru a accepta donatii prin mobilpay acest camp este obligatoriu")
            if not mobilpay_private_key:
                self.add_error('mobilpay_private_key', "Pentru a accepta donatii prin mobilpay acest camp este obligatoriu")
        if accepts_transfer:
            if not donations_description:
                self.add_error('donations_description', "Pentru a accepta donatii prin transfer acest camp este obligatoriu")
            if not cif:
                self.add_error('cif', "Pentru a accepta donatii prin transfer bancar acest camp este obligatoriu")
            if not cui:
                self.add_error('cui', "Pentru a accepta donatii prin transfer bancar acest camp este obligatoriu")
            

class NGORegisterRequestForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"required_score": 0.85,}), label="")

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
            # "has_netopia_contract": forms.CheckboxInput(),
            "avatar": AdminResubmitImageWidget,
            "last_balance_sheet": AdminResubmitFileWidget,
            "statute": AdminResubmitFileWidget,
        }


class RegisterNGORequestVoteForm(forms.ModelForm):
    class Meta:
        model = models.RegisterNGORequestVote
        fields = ("vote", "motivation")
