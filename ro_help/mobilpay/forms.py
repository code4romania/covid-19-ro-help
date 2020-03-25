from django import forms
from django_crispy_bulma.widgets import EmailInput
from mobilpay import models
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class PaymentOrderForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(attrs={"required_score": 0.85,}), label="")

    class Meta:
        model = models.PaymentOrder
        test = forms.CheckboxInput()
        fields = ("amount", "first_name", "last_name", "phone", "email", "address", "show_name")
        widgets = {
            "email": EmailInput(),
            "amount": forms.NumberInput(attrs={"class": "input"}),
            "show_name": forms.CheckboxInput(),
        }
