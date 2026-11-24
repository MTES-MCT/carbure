import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [("transactions", "0022_alter_site_site_type_energyinstallation")]

    operations = [
        migrations.CreateModel(
            name="EnergyInstallation",
            fields=[
                (
                    "site_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="transactions.site",
                    ),
                ),
                (
                    "production_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("ELECTRICITY", "Électricité seule"),
                            ("HEAT", "Chaleur/Froid seul"),
                            ("COGENERATION", "Cogénération"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "heat_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("HOT_WATER", "Eau chaude"),
                            ("STEAM", "Vapeur"),
                            ("HOT_WATER_STEAM", "Eau chaude et vapeur"),
                            ("INDUSTRIAL_PROCESS", "Process industriel"),
                        ],
                        max_length=24,
                        null=True,
                    ),
                ),
                ("useful_temperature", models.FloatField(blank=True, null=True)),
                (
                    "electrical_efficiency",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "thermal_efficiency",
                    models.FloatField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                (
                    "icpe_number",
                    models.CharField(
                        blank=True,
                        max_length=10,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator("^\\d{10}$", "Le numéro ICPE doit comporter 10 chiffres.")
                        ],
                    ),
                ),
                (
                    "icpe_regime",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("AUTHORIZATION", "Autorisation"),
                            ("REGISTRATION", "Enregistrement"),
                            ("DECLARATION_PERIODIC_CONTROLS", "Déclaration (avec contrôles périodiques)"),
                        ],
                        max_length=32,
                        null=True,
                    ),
                ),
                (
                    "producer",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="energy_installation",
                        to="core.entity",
                    ),
                ),
            ],
            options={
                "verbose_name": "Installation de chaleur et d'électricité",
                "db_table": "sites_energyinstallations",
            },
            bases=("transactions.site",),
        ),
    ]
