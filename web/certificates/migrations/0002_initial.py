# Generated by Django 4.1.1 on 2022-09-13 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("producers", "0001_initial"),
        ("core", "0001_initial"),
        ("certificates", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="productionsitecertificate",
            name="certificate",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.entitycertificate"
            ),
        ),
        migrations.AddField(
            model_name="productionsitecertificate",
            name="entity",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.entity"),
        ),
        migrations.AddField(
            model_name="productionsitecertificate",
            name="production_site",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="producers.productionsite"),
        ),
        migrations.AddField(
            model_name="doublecountingregistrationinputoutput",
            name="biofuel",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.biocarburant"),
        ),
        migrations.AddField(
            model_name="doublecountingregistrationinputoutput",
            name="certificate",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="certificates.doublecountingregistration"
            ),
        ),
        migrations.AddField(
            model_name="doublecountingregistrationinputoutput",
            name="feedstock",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.matierepremiere"
            ),
        ),
    ]
