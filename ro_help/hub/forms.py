from django import forms
from django.utils.translation import ugettext_lazy as _
from django_crispy_bulma.forms import EmailField
from django_crispy_bulma.widgets import EmailInput

from hub import models


class NGOHelperForm(forms.ModelForm):

    class Meta:
        model = models.NGOHelper
        fields = ("name", "email", "message", "phone")
        widgets = {
            'email': EmailInput()
        }


class NGORegisterRequestForm(forms.ModelForm):

    class Meta:
        model = models.RegisterNGORequest
        fields = fields = ["name", "county", "city", "address", "avatar", "email", "contact_name",
              "contact_phone", "email", "social_link", "description", "has_netopia_contract"]
        widgets = {
            'email': EmailInput()
        }
