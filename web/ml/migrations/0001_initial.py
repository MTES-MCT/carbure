# Generated by Django 4.1.1 on 2022-09-13 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ETDStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_value', models.FloatField(default=0.0)),
                ('feedstock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.matierepremiere')),
            ],
            options={
                'verbose_name': 'ML ETD Stat',
                'verbose_name_plural': 'ML ETD Stats',
                'db_table': 'ml_etd_stats',
            },
        ),
        migrations.CreateModel(
            name='EPStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nb_lots', models.IntegerField()),
                ('default_value_min_ep', models.FloatField(default=0.0)),
                ('default_value_max_ep', models.FloatField(default=0.0)),
                ('stddev', models.FloatField()),
                ('average', models.FloatField()),
                ('biofuel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.biocarburant')),
                ('feedstock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.matierepremiere')),
            ],
            options={
                'verbose_name': 'ML EP Stat',
                'verbose_name_plural': 'ML EP Stats',
                'db_table': 'ml_ep_stats',
            },
        ),
        migrations.CreateModel(
            name='EECStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nb_lots', models.IntegerField()),
                ('default_value', models.FloatField(default=0.0)),
                ('stddev', models.FloatField()),
                ('average', models.FloatField()),
                ('feedstock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.matierepremiere')),
                ('origin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pays')),
            ],
            options={
                'verbose_name': 'ML EEC Stat',
                'verbose_name_plural': 'ML EEC Stats',
                'db_table': 'ml_eec_stats',
            },
        ),
    ]
