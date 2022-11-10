# Generated by Django 4.1.1 on 2022-10-17 16:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('producers', '0001_initial'),
        ('core', '0004_entity_has_saf_tickets'),
    ]

    operations = [
        migrations.CreateModel(
            name='SafTicketSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carbure_id', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('year', models.IntegerField()),
                ('period', models.IntegerField()),
                ('total_volume', models.FloatField()),
                ('assigned_volume', models.FloatField()),
                ('unknown_producer', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('unknown_production_site', models.CharField(blank=True, default=None, max_length=64, null=True)),
                ('production_site_commissioning_date', models.DateField(blank=True, null=True)),
                ('eec', models.FloatField(default=0.0)),
                ('el', models.FloatField(default=0.0)),
                ('ep', models.FloatField(default=0.0)),
                ('etd', models.FloatField(default=0.0)),
                ('eu', models.FloatField(default=0.0)),
                ('esca', models.FloatField(default=0.0)),
                ('eccs', models.FloatField(default=0.0)),
                ('eccr', models.FloatField(default=0.0)),
                ('eee', models.FloatField(default=0.0)),
                ('ghg_total', models.FloatField(default=0.0)),
                ('ghg_reference', models.FloatField(default=0.0)),
                ('ghg_reduction', models.FloatField(default=0.0)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.entity')),
                ('biofuel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.biocarburant')),
                ('carbure_producer', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='saf_producer', to='core.entity')),
                ('carbure_production_site', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='producers.productionsite')),
                ('country_of_origin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='saf_origin_country', to='core.pays')),
                ('feedstock', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.matierepremiere')),
                ('parent_lot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.carburelot')),
                ('production_country', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='saf_production_country', to='core.pays')),
            ],
            options={
                'verbose_name': 'Source ticket SAF',
                'verbose_name_plural': 'Sources ticket SAF',
                'db_table': 'saf_ticket_source',
                'ordering': ['carbure_id'],
            },
        ),
    ]