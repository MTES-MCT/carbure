# Generated by Django 4.0.2 on 2022-05-13 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0212_alter_carburelotreliabilityscore_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carburelotreliabilityscore',
            name='comment',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]