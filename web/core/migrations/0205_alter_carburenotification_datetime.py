# Generated by Django 4.0.2 on 2022-03-15 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0204_carburenotification_notify_administrator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carburenotification',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
