# Generated by Django 3.0.7 on 2020-07-31 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_pays_is_in_europe'),
    ]

    operations = [
        migrations.AddField(
            model_name='pays',
            name='name_en',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
