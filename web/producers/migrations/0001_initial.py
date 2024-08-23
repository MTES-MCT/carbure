# Generated by Django 4.1.1 on 2022-09-13 10:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('date_mise_en_service', models.DateField()),
                ('ges_option', models.CharField(choices=[('Default', 'Valeurs par défaut'), ('Actual', 'Valeurs réelles'), ('NUTS2', 'Valeurs NUTS2')], default='Default', max_length=12)),
                ('eligible_dc', models.BooleanField(default=False)),
                ('dc_reference', models.CharField(blank=True, default='', max_length=64, null=True)),
                ('site_id', models.CharField(blank=True, max_length=64)),
                ('address', models.CharField(blank=True, default='', max_length=256)),
                ('city', models.CharField(blank=True, max_length=64)),
                ('postal_code', models.CharField(blank=True, max_length=64)),
                ('gps_coordinates', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('manager_name', models.CharField(blank=True, max_length=64)),
                ('manager_phone', models.CharField(blank=True, max_length=64)),
                ('manager_email', models.CharField(blank=True, max_length=64)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pays')),
                ('producer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entity')),
            ],
            options={
                'verbose_name': 'Site de Production',
                'verbose_name_plural': 'Sites de Production',
                'db_table': 'producer_sites',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductionSiteOutput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'En attente de validation'), ('Valid', 'Validé')], default='Pending', max_length=16)),
                ('biocarburant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.biocarburant')),
                ('production_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producers.productionsite')),
            ],
            options={
                'verbose_name': 'Site de Production - Biocarburant',
                'verbose_name_plural': 'Sites de Production - Biocarburants',
                'db_table': 'production_sites_output',
            },
        ),
        migrations.CreateModel(
            name='ProductionSiteInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'En attente de validation'), ('Valid', 'Validé')], default='Pending', max_length=16)),
                ('matiere_premiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.matierepremiere')),
                ('production_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='producers.productionsite')),
            ],
            options={
                'verbose_name': 'Site de Production - Filiere',
                'verbose_name_plural': 'Sites de Production - Filieres',
                'db_table': 'production_sites_input',
            },
        ),
    ]
