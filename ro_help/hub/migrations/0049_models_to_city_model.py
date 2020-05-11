# Custom migration
from django.db import migrations, models
import django.db.models.deletion


def map_city_field_to_city_model(apps, schema_editor):
    print(f"\n{'*'*80}\n")
    print("[INFO]: START of data migration")

    City = apps.get_model("hub", "City")

    NGO = apps.get_model("hub", "NGO")
    NGONeed = apps.get_model("hub", "NGONeed")
    PersonalRequest = apps.get_model("hub", "PersonalRequest")
    RegisterNGORequest = apps.get_model("hub", "RegisterNGORequest")

    models = [NGO, NGONeed, PersonalRequest, RegisterNGORequest]

    for model in models:
        for n in model.objects.all():
            try:
                if "sector" in n.county.lower():
                    n.county = "BUCURESTI"

                city = n.city.lower().strip()
                # remove romanian characters
                for i in [("ț", "t"), ("ș", "s"), ("î", "i"), ("â", "a"), ("ă", "a")]:
                    city = city.replace(i[0], i[1])

                # hack to format cities like "alba-iulia" properly
                city = " ".join(city.split()).replace("-", "  ").title().replace("  ", "-")

                # another fail-safe in case the "sector" one did not catch this
                if city == "Bucuresti":
                    n.county = "BUCURESTI"

                city = City.objects.get(city__iexact=city, county__iexact=n.county)
                n.city_fk = city
                n.save()
                print(f"[INFO]: Migrated: {n}")
            except City.DoesNotExist:
                print(
                    f"[ERROR]: Could not migrate properly: {n}. "
                    f"City object with fields {n.city} ({n.county}) not found."
                )

    print("[INFO]: END of data migration\n")
    print(f"\n{'*'*80}\n")


class Migration(migrations.Migration):

    dependencies = [
        ("hub", "0048_auto_20200429_0736"),
    ]

    operations = [
        migrations.AddField(
            model_name="ngo",
            name="city_fk",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="hub.City", verbose_name="City",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ngoneed",
            name="city_fk",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="hub.City", verbose_name="City",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="personalrequest",
            name="city_fk",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="hub.City", verbose_name="City",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="registerngorequest",
            name="city_fk",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.PROTECT, to="hub.City", verbose_name="City",
            ),
            preserve_default=False,
        ),
        # data migration
        migrations.RunPython(map_city_field_to_city_model),
        migrations.RenameField(model_name="ngo", old_name="city", new_name="city_old", verbose_name="City (legacy)",),
        migrations.RenameField(model_name="ngo", old_name="city_fk", new_name="city",),
        migrations.RenameField(
            model_name="ngoneed", old_name="city", new_name="city_old", verbose_name="City (legacy)",
        ),
        migrations.RenameField(model_name="ngoneed", old_name="city_fk", new_name="city",),
        migrations.RenameField(
            model_name="personalrequest", old_name="city", new_name="city_old", verbose_name="City (legacy)",
        ),
        migrations.RenameField(model_name="personalrequest", old_name="city_fk", new_name="city",),
        migrations.RenameField(
            model_name="registerngorequest", old_name="city", new_name="city_old", verbose_name="City (legacy)",
        ),
        migrations.RenameField(model_name="registerngorequest", old_name="city_fk", new_name="city",),
        migrations.AlterModelOptions(name="city", options={"verbose_name": "City", "verbose_name_plural": "cities"},),
    ]
