# Generated by Django 4.1.7 on 2024-04-23 17:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("elec", "0028_alter_elecmeterreadingapplication_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="elecchargepoint",
            name="previous_version",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="next_version",
                to="elec.elecchargepoint",
            ),
        ),
    ]
