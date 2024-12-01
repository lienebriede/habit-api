# Generated by Django 5.1.3 on 2024-11-30 19:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HabitStacking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habit1', models.CharField(max_length=255)),
                ('habit2', models.CharField(max_length=255)),
                ('goal', models.CharField(choices=[('DAILY', 'Daily'), ('NO_GOAL', 'No Goal')], default='DAILY', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'habit1', 'habit2', 'goal')},
            },
        ),
    ]