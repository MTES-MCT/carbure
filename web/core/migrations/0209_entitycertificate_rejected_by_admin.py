# Generated by Django 4.0.2 on 2022-04-13 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0208_entitycertificate_added_dt'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitycertificate',
            name='rejected_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
