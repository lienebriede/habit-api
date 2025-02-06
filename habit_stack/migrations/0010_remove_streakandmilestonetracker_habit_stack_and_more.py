# Generated by Django 5.1.3 on 2025-01-23 22:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habit_stack', '0009_remove_habitstacking_goal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='streakandmilestonetracker',
            name='habit_stack',
        ),
        migrations.RemoveField(
            model_name='streakandmilestonetracker',
            name='user',
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_achieved', models.DateField()),
                ('description', models.CharField(max_length=255)),
                ('habit_stack', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='habit_stack.habitstacking')),
            ],
        ),
        migrations.DeleteModel(
            name='MilestonePost',
        ),
        migrations.DeleteModel(
            name='StreakAndMilestoneTracker',
        ),
    ]
