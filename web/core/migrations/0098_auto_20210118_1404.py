# Generated by Django 3.0.7 on 2021-01-18 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_userrightsrequests'),
    ]

    operations = [
        migrations.CreateModel(
            name='Control',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('OPEN', 'Ouvert'), ('CLOSED', 'Clôturé')], default='OPEN', max_length=32)),
                ('opened_at', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('tx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.LotTransaction')),
            ],
            options={
                'verbose_name': 'Contrôle Lot',
                'verbose_name_plural': 'Contrôles Lots',
                'db_table': 'controls',
            },
        ),
        migrations.AlterField(
            model_name='userrightsrequests',
            name='status',
            field=models.CharField(choices=[('PENDING', 'En attente de validation'), ('ACCEPTED', 'Accepté'), ('REJECTED', 'Refusé'), ('REVOKED', 'Révoqué')], default='PENDING', max_length=32),
        ),
        migrations.CreateModel(
            name='ControlFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Control')),
            ],
            options={
                'verbose_name': 'Contrôle - Justificatif',
                'verbose_name_plural': 'Contrôles - Justificatifs',
                'db_table': 'control_files',
            },
        ),
    ]
