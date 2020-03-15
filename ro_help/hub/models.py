from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


class URGENCY:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @classmethod
    def to_choices(cls):
        return [
            (URGENCY.CRITICAL, URGENCY.CRITICAL),
            (URGENCY.HIGH, URGENCY.HIGH),
            (URGENCY.MEDIUM, URGENCY.MEDIUM),
            (URGENCY.LOW, URGENCY.LOW),
        ]

    @classmethod
    def default(cls):
        return URGENCY.LOW

    @classmethod
    def to_list(cls):
        return [URGENCY.CRITICAL, URGENCY.HIGH, URGENCY.MEDIUM, URGENCY.LOW]


class KIND:
    RESOURCE = "resource"
    VOLUNTEER = "volunteer"
    MONEY = "money"

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


class NGO(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=254)
    description = models.CharField(_("Description"), max_length=2048)
    email = models.EmailField(_("Email"),)
    phone = models.CharField(_("Phone"), max_length=30)
    avatar = models.ImageField(_("Avatar"), max_length=300)
    address = models.CharField(_("Address"), max_length=400)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), max_length=50)

    def __str__(self):
        return self.name


class NGONeedQuerySet(models.QuerySet):
    def active(self):
        return self.filter(resolved_on=None)

    def resolved(self):
        return self.exclude(resolved_on=None)

    def money(self):
        return self.active().filter(kind=KIND.MONEY)

    def resource(self):
        return self.active().filter(kind=KIND.RESOURCE)

    def volunteer(self):
        return self.active().filter(kind=KIND.VOLUNTEER)


class NGONeed(TimeStampedModel):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name="needs")

    title = models.CharField(_("Title"), max_length=254)
    description = models.CharField(_("Description"), max_length=4096)

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(), default=URGENCY.default(), max_length=10)

    resolved_on = models.DateTimeField(_("Resolved on"), null=True, blank=True)

    objects = NGONeedQuerySet.as_manager()

    def __str__(self):
        return f"{self.ngo.name}: {self.urgency} {self.kind}"


class PersonalRequest(TimeStampedModel):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, null=True, blank=True, related_name="requests")

    name = models.CharField(_("Name"), max_length=254,)
    email = models.EmailField(_("Email"), null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=15)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), max_length=50)
    address = models.CharField(_("Address"), max_length=400, null=True, blank=True)
    organization = models.CharField(_("Organization"), max_length=400, null=True, blank=True)
    description = models.CharField(_("Description"), max_length=1024)

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(), default=URGENCY.default(), max_length=10)

    def __str__(self):
        return self.name
