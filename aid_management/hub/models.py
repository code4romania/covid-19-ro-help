from django.db import models
from django.utils.translation import ugettext_lazy as _


class KIND:
    RESOURCE = "resource"
    VOLUNTEER = "volunteer"
    MONEY = "Money"

    @classmethod
    def to_choices(cls):
        return [
            (KIND.RESOURCE, KIND.RESOURCE),
            (KIND.VOLUNTEER, KIND.VOLUNTEER),
            (KIND.MONEY, KIND.MONEY),
        ]

    @classmethod
    def default(cls):
        return KIND.RESOURCE

    @classmethod
    def to_list(cls):
        return [KIND.RESOURCE, KIND.VOLUNTEER, KIND.MONEY]


class NGO(models.Model):
    name = models.CharField(_("Name"), max_length=254,)
    description = models.CharField(_("Description"), max_length=1024)
    email = models.EmailField(_("Email"), )
    phone = models.CharField(_("Phone"), max_length=15)
    avatar = models.ImageField(_("Avatar"), max_length=15)
    address = models.CharField(_("Address"), max_length=400)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), max_length=50)


# class NGONeed(models.Model):
#     ngo = models.ForeignKey(NGO, on_delete=models.CASCADE)
#     description = models.CharField(_("Description"), )
#     kind = models.Choices(_())
