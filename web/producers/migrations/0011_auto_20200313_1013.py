# Generated by Django 3.0.3 on 2020-03-13 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producers', '0010_auto_20200304_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionsiteinput',
            name='status',
            field=models.CharField(choices=[('Pending', 'En attente de validation'), ('Valid', 'Validé')], default='Pending', max_length=16),
        ),
        migrations.AddField(
            model_name='productionsiteoutput',
            name='status',
            field=models.CharField(choices=[('Pending', 'En attente de validation'), ('Valid', 'Validé')], default='Pending', max_length=16),
        ),
        migrations.AlterField(
            model_name='productionsiteoutput',
            name='ges_option',
            field=models.CharField(choices=[('Default', 'Valeurs par défaut'), ('Actual', 'Valeurs réelles')], default='Default', max_length=12),
        ),
    ]
