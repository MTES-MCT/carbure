# Generated by Django 3.0.3 on 2020-03-12 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('producers', '0010_auto_20200304_1639'),
        ('core', '0014_auto_20200303_1216'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lot',
            old_name='num_dae',
            new_name='dae',
        ),
        migrations.RenameField(
            model_name='lot',
            old_name='date_entree',
            new_name='ea_delivery_date',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='affiliate',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='categorie',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='date_mise_en_service',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='depot',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='ges_fossile',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='ges_transport_distrib',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='pays_production',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='respect_crit_durabilite',
        ),
        migrations.RemoveField(
            model_name='lot',
            name='systeme_fournisseur',
        ),
        migrations.AddField(
            model_name='lot',
            name='client_id',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='lot',
            name='e',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='ea',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ea', to='core.Entity'),
        ),
        migrations.AddField(
            model_name='lot',
            name='ea_delivery_site',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='lot',
            name='eccr',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='eccs',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='eec',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='eee',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='el',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='ep',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='esca',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='etd',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='eu',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='ghg_reduction',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='ghg_reference',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='lot',
            name='production_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='producers.ProductionSite'),
        ),
        migrations.AlterField(
            model_name='lot',
            name='status',
            field=models.CharField(choices=[('Draft', 'Draft'), ('Validated', 'Validated')], default='Draft', max_length=64),
        ),
    ]
