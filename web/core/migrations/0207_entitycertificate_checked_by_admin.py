# Generated by Django 4.0.2 on 2022-03-24 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0206_alter_carburenotification_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitycertificate',
            name='checked_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
