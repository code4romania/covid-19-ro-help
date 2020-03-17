from django.db import models
from django.contrib.auth.models import User
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
        return KIND.MONEY

    @classmethod
    def to_list(cls):
        return [KIND.RESOURCE, KIND.VOLUNTEER, KIND.MONEY]


class COUNTY:
    counties = ["ALBA", "ARGES", "ARAD", "BACAU", "BIHOR", "BISTRITA-NASAUD", "BRAILA", "BRASOV", "BOTOSANI", "BUZAU", "CLUJ", "CALARASI", "CARAS-SEVERIN", "CONSTANTA", "COVASNA", "DAMBOVITA", "DOLJ", "GORJ", "GALATI", "GIURGIU",
                "HUNEDOARA", "HARGHITA", "IALOMITA", "IASI", "MEHEDINTI", "MARAMURES", "MURES", "NEAMT", "OLT", "PRAHOVA", "SIBIU", "SALAJ", "SATU-MARE", "SUCEAVA", "TULCEA", "TIMIS", "TELEORMAN", "VALCEA", "VRANCEA", "VASLUI", "ILFOV", "BUCURESTI", "SECTOR 1", "SECTOR 2", "SECTOR 3", "SECTOR 4", "SECTOR 5", "SECTOR 6"]

    @classmethod
    def to_choices(cls):
        return [(x, x) for x in cls.counties]

    @classmethod
    def default(cls):
        return cls.counties[0]

    @classmethod
    def to_list(cls):
        return cls.counties


class NGO(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=254)
    users = models.ManyToManyField(User, related_name="ngos")
    description = models.TextField(_("Description"))
    email = models.EmailField(_("Email"),)
    phone = models.CharField(_("Phone"), max_length=30)
    avatar = models.ImageField(_("Avatar"), max_length=300)
    address = models.CharField(_("Address"), max_length=400)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(
        _("County"), choices=COUNTY.to_choices(), max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "ONG-uri"


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
    ngo = models.ForeignKey(
        NGO, on_delete=models.CASCADE, related_name="needs")

    title = models.CharField(_("Title"), max_length=254)
    description = models.TextField(_("Description"))

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(
    ), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(
    ), default=URGENCY.default(), max_length=10)

    resolved_on = models.DateTimeField(_("Resolved on"), null=True, blank=True)

    objects = NGONeedQuerySet.as_manager()

    def __str__(self):
        return f"{self.ngo.name}: {self.urgency} {self.kind}"

    class Meta:
        verbose_name_plural = "Nevoi ONG"
        verbose_name = "Nevoie ONG"




class NGOHelper(TimeStampedModel):
    ngo_need = models.ForeignKey(
        NGONeed, on_delete=models.CASCADE, related_name="helpers")

    name = models.CharField(_("Name"), max_length=254)
    email = models.EmailField(_("Email"),)
    message = models.TextField(_("Message"))
    phone = models.CharField(_("Phone"), max_length=30, null=True, blank=True)

    read = models.BooleanField(_("Read on"), null=True, blank=True)


class PersonalRequest(TimeStampedModel):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE,
                            null=True, blank=True, related_name="requests")

    name = models.CharField(_("Name"), max_length=254,)
    email = models.EmailField(_("Email"), null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=15)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(
        _("County"), choices=COUNTY.to_choices(), max_length=50)
    address = models.CharField(
        _("Address"), max_length=400, null=True, blank=True)
    organization = models.CharField(
        _("Organization"), max_length=400, null=True, blank=True)
    description = models.TextField(_("Description"))

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(
    ), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(
    ), default=URGENCY.default(), max_length=10)

    def __str__(self):
        return self.name


class RegisterNGORequest(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=254)
    coverage = models.CharField(_("Coverage"), max_length=254, help_text=_("Country or county/city selection"))
    email = models.EmailField(_("Email"), null=True, blank=True)

    contact_name = models.CharField(_("Contact person's name"), max_length=254)
    contact_phone = models.CharField(_("Contact person's phone"), max_length=15)

    has_netopia_contract = models.BooleanField(_("Has contract with Netopia"), default=False)
    social_link = models.CharField(_("Link to website or Facebook"), max_length=512, null=True, blank=True)

    description = models.TextField(
        _("Description"), max_length=500, help_text=_("Organization's short description - max 500 chars.")
    )
