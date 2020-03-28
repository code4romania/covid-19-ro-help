from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class PasswordDifferentFromPrevious:
    def validate(self, password, user=None):
        if not user:
            return

        # If the newly provided password is in fact still the old password
        # consider it invalid
        if check_password(password, user.password):
            raise ValidationError(
                _("Your new password must be different."),
            )

    def get_help_text(self):
        return _("Please correct the error below. Your new password must be different. Please try again.")
