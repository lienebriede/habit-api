# Generated by Django 3.2.4 on 2025-03-15 20:27

from django.db import migrations, models
import habit_stack.models


class Migration(migrations.Migration):

    dependencies = [
        ('habit_stack', '0010_remove_streakandmilestonetracker_habit_stack_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habitstacking',
            name='active_until',
            field=models.DateField(default=habit_stack.models.HabitStacking.default_active_until),
        ),
    ]
