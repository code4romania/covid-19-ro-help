import random

import requests
from faker import Faker

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone

from hub.models import (
    NGO,
    NGONeed,
    NGOHelper,
    NGOAccount,
    PendingRegisterNGORequest,
    RegisterNGORequest,
    RegisterNGORequestVote,
    KIND,
    URGENCY,
    ResourceTag,
    ADMIN_GROUP_NAME,
    NGO_GROUP_NAME,
    DSU_GROUP_NAME,
    FFC_GROUP_NAME,
    NGOReportItem,
)
from mobilpay.models import PaymentOrder


fake = Faker()


def random_avatar():
    try:
        image = requests.get("https://source.unsplash.com/random", allow_redirects=False)
        return image.headers["Location"]
    except:
        return "https://source.unsplash.com/random"


NGOS = (
    [
        {
            "name": "Habitat for Humanity",
            "email": "habitat@habitat.ro",
            "description": """
        O locuință decentă poate rupe cercul sărăciei. Credem cu tărie în acest lucru din 1976, de când lucrăm pentru 
        viziunea noastră: o lume în care toți oamenii au posibilitatea să locuiască decent. Cu sprijinul nostru,
        peste 6 milioane de oameni din peste 70 de țări au un loc mai bun în care să trăiască, o casă nouă sau una
        complet renovată.Suntem o asociație creștină, non-profit, ce lucrăm alături de oameni de pretutindeni, 
        din toate păturile sociale, rasele, religiile și naționalitățile pentru a elimina locuirea precară.
        """,
            "phone": "+40722644394",
            "address": "Str. Naum Râmniceanu, nr. 45 A, et.1, ap. 3, sector 1, Bucureşti 011616",
            "city": "Bucureşti",
            "county": "Sector 1",
            "avatar": "http://www.habitat.ro/wp-content/uploads/2014/11/logo.png",
        },
        {
            "name": "Crucea Rosie",
            "email": "matei@crucearosie.ro",
            "description": """
         Crucea Rosie Romana asista persoanele vulnerabile in situatii de dezastre si de criza. Prin programele si 
         activitatile sale in beneficiul societatii, contribuie la prevenirea si alinarea suferintei sub toate formele,
          protejeaza sanatatea si viata, promoveaza respectul fata de demnitatea umana, fara nicio discriminare bazata 
          pe nationalitate, rasa, sex, religie, varsta, apartenenta sociala sau politica.
        """,
            "phone": "+40213176006",
            "address": "Strada Biserica Amzei, nr. 29, Sector 1, Bucuresti",
            "city": "Bucuresti",
            "county": "Sector 1",
            "avatar": "https://crucearosie.ro/themes/redcross/images/emblema_crr_desktop.png",
        },
        {
            "name": "MKBT: Make Better",
            "email": "contact@mkbt.ro",
            "description": """
        MKBT: Make Better has been working for urban development and regeneration in Romania since April 2014. 
        That is to say that we are drafting, validating and coordinating processes for local development and urban 
        regeneration in order to help as many cities become their best possible version and the best home for their inhabitants.
        As a local development advisor, we assist both public and private entities.
        We substantiate our work on a thorough understanding of local needs and specificities of the communities we 
        work with. We acknowledge, at the same time, the global inter-connectivity of local challenges. Our proposed 
        solutions are therefore grounded in international best practice, while at the same time capitalizing – in a
         sustainable and harmonious manner – on local know how and resources.
        """,
            "phone": "+40213176006",
            "address": "Str. Popa Petre, Nr. 23, Sector 2, 020802, Bucharest, Romania.",
            "city": "Bucuresti",
            "county": "Sector 2",
            "avatar": "http://mkbt.ro/wp-content/uploads/2015/08/MKBT-logo-alb.png",
        },
    ]
    + [
        {
            "name": fake.name(),
            "email": fake.email(),
            "description": fake.text(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "city": random.choice(["Arad", "Timisoara", "Oradea", "Cluj", "Bucuresti"]),
            "county": random.choice(["ARAD", "TIMIS", "BIHOR", "CLUJ", "SECTOR 1", "SECTOR 2"]),
            "avatar": random_avatar(),
        }
        for _ in range(2)
    ]
)


RESOURCE_TAGS = ["apa", "ceai", "manusi de protectie"]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_user("admin", "admin@admin.com", "admin", is_staff=True, is_superuser=True)

        if not User.objects.filter(username="user").exists():
            User.objects.create_user("user", "user@user.com", "user", is_staff=True)

        if not User.objects.filter(username="dsu").exists():
            User.objects.create_user("dsu", "user@user.com", "dsu", is_staff=True)

        if not User.objects.filter(username="ffc").exists():
            User.objects.create_user("ffc", "user@user.com", "ffc", is_staff=True)

        admin_user = User.objects.get(username="admin")
        ngo_user = User.objects.get(username="user")
        dsu_user = User.objects.get(username="dsu")
        ffc_user = User.objects.get(username="ffc")

        admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)
        ngo_group, _ = Group.objects.get_or_create(name=NGO_GROUP_NAME)
        dsu_group, _ = Group.objects.get_or_create(name=DSU_GROUP_NAME)
        ffc_group, _ = Group.objects.get_or_create(name=FFC_GROUP_NAME)

        # models.NamedCredentials: ['add', 'change', 'delete', 'view'],
        GROUPS_PERMISSIONS = {
            NGO_GROUP_NAME: {
                NGO: ["change", "view"],
                NGOHelper: ["view"],
                NGONeed: ["add", "change", "view"],
                NGOReportItem: ["add", "change", "delete", "view"],
                NGOAccount: ["add", "change", "delete", "view"],
            },
            DSU_GROUP_NAME: {
                PendingRegisterNGORequest: ["view", "change"],
                RegisterNGORequest: ["view"],
                RegisterNGORequestVote: ["view", "change"],
            },
            FFC_GROUP_NAME: {
                PendingRegisterNGORequest: ["view", "change"],
                RegisterNGORequest: ["view"],
                RegisterNGORequestVote: ["view", "change"],
            },
        }

        for group_name in GROUPS_PERMISSIONS:

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(GROUPS_PERMISSIONS[group_name][model_cls]):

                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name

                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write("Adding " + codename + " to group " + group.__str__())
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + " not found")

        admin_user.groups.add(admin_group)
        admin_user.save()

        ngo_user.groups.add(ngo_group)
        ngo_user.save()

        dsu_user.groups.add(dsu_group)
        dsu_user.save()

        ffc_user.groups.add(ffc_group)
        ffc_user.save()

        tags = []
        for resource in RESOURCE_TAGS:
            tag, _ = ResourceTag.objects.get_or_create(name=resource)
            tags.append(tag)

        NGO.objects.filter(
            pk__in=NGO.objects.exclude(name__in=["Code4Romania", "Crucea Rosie"])
            .order_by("created")
            .values_list("pk")[100:]
        ).delete()

        for details in NGOS:
            ngo, _ = NGO.objects.get_or_create(**details)

            owner = random.choice([ngo_user, admin_user, None])
            if owner:
                ngo.users.add(owner)
                ngo.save()


            for _ in range(20):
                need = NGONeed.objects.create(
                    **{
                        "ngo": ngo,
                        "kind": random.choice(["volunteer", "resource"]),
                        "urgency": random.choice(URGENCY.to_list()),
                        "description": fake.text(),
                        "title": fake.text(),
                        "resolved_on": random.choice([None, timezone.now()]),
                        "city": random.choice(["Arad", "Timisoara", "Oradea", "Cluj", "Bucuresti"]),
                        "county": random.choice(["ARAD", "TIMIS", "BIHOR", "CLUJ", "SECTOR 1", "SECTOR 2"]),
                    }
                )

                for _ in range(len(RESOURCE_TAGS)):
                    need.resource_tags.add(random.choice(tags))
            NGONeed.objects.filter(pk__in=ngo.needs.order_by("created").values_list("pk")[20:]).delete()

        for ngo in NGO.objects.all():
            for _ in range(random.choice([3, 4, 5, 6, 10])):
                PaymentOrder.objects.create(
                    ngo=ngo,
                    first_name=fake.name().split(" ")[0],
                    last_name=fake.name().split(" ")[-1],
                    phone=fake.phone_number(),
                    email=fake.email(),
                    address=fake.address(),
                    details="ddd",
                    amount=random.choice([100, 200, 300, 400, 500, 150]),
                    date=fake.date_between(start_date="-30y", end_date="today"),
                    success=True,
                )
            PaymentOrder.objects.filter(
                pk__in=PaymentOrder.objects.filter(ngo=ngo).order_by("created").values_list("pk")[10:]
            ).delete()


            for _ in range(random.choice([3, 4, 5, 6, 10])):
                NGOReportItem.objects.create(
                    ngo=ngo,
                    date=fake.date_between(start_date="-30y", end_date="today"),
                    title=f"Achizitionat {random.choice(RESOURCE_TAGS)}",
                    amount=random.choice([100, 200, 300, 400, 500, 150]),
                )
            NGOReportItem.objects.filter(
                pk__in=NGOReportItem.objects.filter(ngo=ngo).order_by("created").values_list("pk")[10:]
            ).delete()
