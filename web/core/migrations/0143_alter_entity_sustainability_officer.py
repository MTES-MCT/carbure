# Generated by Django 3.2 on 2021-05-13 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0142_auto_20210510_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='sustainability_officer',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
    ]
