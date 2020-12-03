# Generated by Django 3.0.7 on 2020-12-03 16:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0096_auto_20201202_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRightsRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'En attente de validation'), ('ACCEPTED', 'Acceoté'), ('REJECTED', 'Refusé'), ('REVOKED', 'Révoqué')], default='PENDING', max_length=32)),
                ('comment', models.TextField(blank=True, null=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Entity')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Right Request',
                'verbose_name_plural': 'Users Rights Requests',
                'db_table': 'users_rights_requests',
            },
        ),
    ]
