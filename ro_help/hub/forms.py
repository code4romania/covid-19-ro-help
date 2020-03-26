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
