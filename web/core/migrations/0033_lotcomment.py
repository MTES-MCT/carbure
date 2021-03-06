# Generated by Django 3.0.3 on 2020-04-20 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_auto_20200420_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='LotComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Lot')),
            ],
            options={
                'verbose_name': 'LotComment',
                'verbose_name_plural': 'LotComments',
                'db_table': 'lots_comments',
            },
        ),
    ]
