# Generated by Django 3.0.7 on 2020-11-20 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0091_entity_national_system_certificate'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbscertificate',
            name='download_link',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AddField(
            model_name='iscccertificate',
            name='download_link',
            field=models.CharField(default='', max_length=512),
        ),
    ]
