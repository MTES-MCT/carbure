# Generated by Django 4.0.2 on 2022-05-09 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0209_entitycertificate_rejected_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='carburelot',
            name='audit_status',
            field=models.CharField(choices=[('UNKNOWN', 'UNKNOWN'), ('CONFORM', 'CONFORM'), ('NONCONFORM', 'NONCONFORM')], default='UNKNOWN', max_length=24),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='ml_control_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='random_control_requested',
            field=models.BooleanField(default=False),
        ),
    ]
