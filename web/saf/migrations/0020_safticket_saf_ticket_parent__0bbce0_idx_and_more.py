# Generated by Django 4.1.1 on 2023-01-30 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("saf", "0019_safticketsource_parent_ticket"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="safticket",
            index=models.Index(
                fields=["parent_ticket_source"], name="saf_ticket_parent__0bbce0_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="safticketsource",
            index=models.Index(
                fields=["parent_lot"], name="saf_ticket__parent__45fd32_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="safticketsource",
            index=models.Index(
                fields=["parent_ticket"], name="saf_ticket__parent__947918_idx"
            ),
        ),
    ]