from django import forms
from django.core.files.images import get_image_dimensions
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

    def clean_avatar(self):
        avatar = self.cleaned_data['avatar']

        try:
            w, h = get_image_dimensions(avatar)

            #validate dimensions
            max_width = max_height = 500
            if w > max_width or h > max_height:
                raise forms.ValidationError(u'Please use an image that is '
                                            '%s x %s pixels or smaller.' %
                                            (max_width, max_height))

            #validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image'
                    and sub in ['jpeg', 'pjpeg', 'png']):
                raise forms.ValidationError(u'Please use a JPEG or PNG image.')
        
        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass
        
        return avatar


class RegisterNGORequestVoteForm(forms.ModelForm):
    class Meta:
        model = models.RegisterNGORequestVote
        fields = ("vote", "motivation")
