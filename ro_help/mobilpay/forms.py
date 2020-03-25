from django import forms
from django_crispy_bulma.widgets import EmailInput
from mobilpay import models
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class PaymentOrderForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV3(
        attrs={"required_score": 0.85, }), label="")
    # amount = forms.Input()
    # amount.widget.attrs.update({'class': 'input'})
    test = forms.CheckboxInput()

    class Meta:
        model = models.PaymentOrder
        fields = ("amount", "test", "first_name", "last_name", "show_name", "phone", "email", "address")
        widgets = {
            "email": EmailInput(),
            "amount": forms.NumberInput(attrs={'class': 'input'}),
            "show_name": forms.CheckboxInput()
            }
