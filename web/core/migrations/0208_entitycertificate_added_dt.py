# Generated by Django 4.0.2 on 2022-03-24 09:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0207_entitycertificate_checked_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitycertificate',
            name='added_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
