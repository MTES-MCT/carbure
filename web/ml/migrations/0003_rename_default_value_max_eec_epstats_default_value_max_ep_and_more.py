# Generated by Django 4.0.2 on 2022-03-29 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ml', '0002_alter_eecstats_default_value_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='epstats',
            old_name='default_value_max_eec',
            new_name='default_value_max_ep',
        ),
        migrations.RenameField(
            model_name='epstats',
            old_name='default_value_min_eec',
            new_name='default_value_min_ep',
        ),
    ]
