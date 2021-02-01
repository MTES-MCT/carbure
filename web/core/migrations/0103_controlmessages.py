# Generated by Django 3.0.7 on 2021-02-01 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0102_sustainabilitydeclaration_declared'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlMessages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('dt_added', models.DateTimeField(auto_now_add=True)),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Control')),
                ('entity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Entity')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contrôle - Message',
                'verbose_name_plural': 'Contrôles - Messages',
                'db_table': 'control_messages',
            },
        ),
    ]
