from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from django_extensions.db.models import TimeStampedModel


ADMIN_GROUP_NAME = "Admin"
NGO_GROUP_NAME = "ONG"


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
    counties = [
        "ALBA",
        "ARGES",
        "ARAD",
        "BACAU",
        "BIHOR",
        "BISTRITA-NASAUD",
        "BRAILA",
        "BRASOV",
        "BOTOSANI",
        "BUCURESTI",
        "BUZAU",
        "CLUJ",
        "CALARASI",
        "CARAS-SEVERIN",
        "CONSTANTA",
        "COVASNA",
        "DAMBOVITA",
        "DOLJ",
        "GORJ",
        "GALATI",
        "GIURGIU",
        "HUNEDOARA",
        "HARGHITA",
        "IALOMITA",
        "IASI",
        "ILFOV",
        "MEHEDINTI",
        "MARAMURES",
        "MURES",
        "NEAMT",
        "OLT",
        "PRAHOVA",
        "SIBIU",
        "SALAJ",
        "SATU-MARE",
        "SECTOR 1",
        "SECTOR 2",
        "SECTOR 3",
        "SECTOR 4",
        "SECTOR 5",
        "SECTOR 6",
        "SUCEAVA",
        "TULCEA",
        "TIMIS",
        "TELEORMAN",
        "VALCEA",
        "VRANCEA",
        "VASLUI",
    ]

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
    county = models.CharField(_("County"), choices=COUNTY.to_choices(), max_length=50)

    # mobilpay_username = models.CharField(_("mobilpay Merchant identifier code"), max_length=20, null=True, blank=True)
    # mobilpay_icc = models.CharField(_("mobilpay Merchant identifier code"), max_length=20, null=True, blank=True)
    mobilpay_icc = models.CharField(_("mobilpay Merchant identifier code"), max_length=24, null=True, blank=True, help_text=_("XXXX-XXXX-XXXX-XXXX-XXXX"))
    mobilpay_public_key = models.FileField(_("mobilpay Public key"), max_length=300, null=True, blank=True)
    mobilpay_private_key = models.FileField(_("mobilpay Private key"), max_length=300, null=True, blank=True)
    
    def __str__(self):
        return self.name

    def get_avatar(self):
        if self.avatar:
            if "http" in str(self.avatar):
                return str(self.avatar)
            return f"{self.avatar.url}"
        else:
            return None

    class Meta:
        verbose_name_plural = _("NGOs")
        verbose_name = _("NGO")


class ResourceTag(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=30)

    def __str__(self):
        return self.name


class NGONeedQuerySet(models.QuerySet):
    def active(self):
        return self.filter(resolved_on=None).filter(closed_on=None)

    def resolved(self):
        return self.exclude(resolved_on=None)

    def closed(self):
        return self.exclude(closed_on=None)

    def money(self):
        return self.active().filter(kind=KIND.MONEY)

    def resource(self):
        return self.active().filter(kind=KIND.RESOURCE)

    def volunteer(self):
        return self.active().filter(kind=KIND.VOLUNTEER)


class NGONeed(TimeStampedModel):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, related_name="needs", verbose_name=_("NGO"))

    title = models.CharField(_("Title"), max_length=254)
    description = models.TextField(_("Description"))

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(), default=URGENCY.default(), max_length=10)

    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), choices=COUNTY.to_choices(), max_length=50)

    resource_tags = models.ManyToManyField("ResourceTag", blank=True, related_name="needs")

    resolved_on = models.DateTimeField(_("Resolved on"), null=True, blank=True)
    closed_on = models.DateTimeField(_("Closed on"), null=True, blank=True)

    objects = NGONeedQuerySet.as_manager()

    def __str__(self):
        return f"{self.ngo.name}: {self.urgency} {self.kind}"

    class Meta:
        verbose_name_plural = _("NGO needs")
        verbose_name = _("NGO need")


class NGOHelper(TimeStampedModel):
    ngo_need = models.ForeignKey(NGONeed, on_delete=models.CASCADE, related_name="helpers")

    name = models.CharField(_("Name"), max_length=254)
    email = models.EmailField(_("Email"),)
    message = models.TextField(_("Message"))
    phone = models.CharField(_("Phone"), max_length=30, null=True, blank=True)

    read = models.BooleanField(_("Read on"), default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = _("NGO Helper")
        verbose_name = _("NGO Helpers")


class PersonalRequest(TimeStampedModel):
    ngo = models.ForeignKey(NGO, on_delete=models.CASCADE, null=True, blank=True, related_name="requests")

    name = models.CharField(_("Name"), max_length=254,)
    email = models.EmailField(_("Email"), null=True, blank=True)
    phone = models.CharField(_("Phone"), max_length=15)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), choices=COUNTY.to_choices(), max_length=50)
    address = models.CharField(_("Address"), max_length=400, null=True, blank=True)
    organization = models.CharField(_("Organization"), max_length=400, null=True, blank=True)
    description = models.TextField(_("Description"))

    kind = models.CharField(_("Kind"), choices=KIND.to_choices(), default=KIND.default(), max_length=10)
    urgency = models.CharField(_("Urgency"), choices=URGENCY.to_choices(), default=URGENCY.default(), max_length=10)

    def __str__(self):
        return self.name


class RegisterNGORequest(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=254)
    description = models.TextField(
        _("Description"), max_length=500, help_text=_("Organization's short description - max 500 chars.")
    )
    contact_name = models.CharField(_("Contact person's name"), max_length=254)
    email = models.EmailField(_("Email"), default="")
    contact_phone = models.CharField(_("Contact person's phone"), max_length=15)
    has_netopia_contract = models.BooleanField(_("Has contract with Netopia"), default=False)
    avatar = models.ImageField(_("Avatar"), max_length=300)
    address = models.CharField(_("Address"), max_length=400)
    city = models.CharField(_("City"), max_length=100)
    county = models.CharField(_("County"), choices=COUNTY.to_choices(), max_length=50)

    social_link = models.CharField(_("Link to website or Facebook"), max_length=512, null=True, blank=True)

    active = models.BooleanField(_("Active"), default=False)
    resolved_on = models.DateTimeField(_("Resolved on"), null=True, blank=True)
    registered_on = models.DateTimeField(_("Registered on"), auto_now_add=True)

    def create_ngo_owner(self, request, ngo_group):
        user, created = User.objects.get_or_create(username=self.email)

        if not created:
            return user

        user.first_name = " ".join(self.contact_name.split(" ")[0:-1])
        user.last_name = self.contact_name.split(" ")[-1]
        user.email = self.email
        user.set_password(get_random_string())
        user.is_staff = True
        user.groups.add(ngo_group)
        user.save()

        reset_form = PasswordResetForm({"email": user.email})
        assert reset_form.is_valid()

        reset_form.save(
            request=request,
            use_https=request.is_secure(),
            subject_template_name="registration/password_reset_subject.txt",
            email_template_name="registration/password_reset_email.html",
        )

        return user

    @transaction.atomic
    def activate(self, request, ngo_group=None):
        ngo_group = ngo_group or Group.objects.get(name=NGO_GROUP_NAME)

        ngo, _ = NGO.objects.get_or_create(
            name=self.name,
            description=self.description,
            email=self.email,
            phone=self.contact_phone,
            avatar=self.avatar,
            address=self.address,
            city=self.city,
            county=self.county,
        )

        owner = self.create_ngo_owner(request, ngo_group)
        ngo.users.add(owner)

        self.resolved_on = timezone.now()
        self.active = True
        self.save()

    def __str__(self):
        return self.name
