# Generated by Django 3.2 on 2021-05-21 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0150_alter_lotv2_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionupdatehistory',
            name='modified_by_entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.entity'),
        ),
    ]
