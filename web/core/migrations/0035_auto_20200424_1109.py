# Generated by Django 3.0.3 on 2020-04-24 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_lotcomment_entity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lot',
            name='ea_delivery_status',
            field=models.CharField(choices=[('N', 'N/A'), ('A', 'Accepté'), ('R', 'Refusé'), ('AC', 'À corriger'), ('AA', 'En attente de validation')], default='N', max_length=64),
        ),
    ]
