# Generated by Django 4.1.1 on 2022-10-20 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("saf", "0003_safticket_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="safticketsource",
            options={
                "ordering": ["carbure_id"],
                "verbose_name": "Tickets source SAF",
                "verbose_name_plural": "Tickets source SAF",
            },
        ),
        migrations.AlterField(
            model_name="safticket",
            name="agreement_date",
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]