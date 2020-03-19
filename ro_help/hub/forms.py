from django import forms

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
        fields = ["name", "county", "city", "address", "avatar", "email", "contact_name",
                  "contact_phone", "email", "social_link", "description", "has_netopia_contract"]
        widgets = {
            'email': EmailInput()
        }
