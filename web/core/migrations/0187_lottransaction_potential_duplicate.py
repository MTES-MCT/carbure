# Generated by Django 3.2.8 on 2021-10-15 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0186_auto_20210927_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='lottransaction',
            name='potential_duplicate',
            field=models.BooleanField(default=False),
        ),
    ]
