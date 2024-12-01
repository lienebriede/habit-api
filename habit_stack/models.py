from django.db import models
from django.contrib.auth.models import User

class PredefinedHabit(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class HabitStacking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predefined_habit1 = models.ForeignKey(PredefinedHabit, null=True, blank=True, on_delete=models.SET_NULL, related_name='habit1_set')
    custom_habit1 = models.CharField(max_length=255, blank=True)
    predefined_habit2 = models.ForeignKey(PredefinedHabit, null=True, blank=True, on_delete=models.SET_NULL, related_name='habit2_set')
    custom_habit2 = models.CharField(max_length=255, blank=True)

    GOAL_CHOICES = [
        ('DAILY', 'Daily'),
        ('NO_GOAL', 'No Goal'),
    ]
    goal = models.CharField(
        max_length=20,
        choices=GOAL_CHOICES,
        default='DAILY'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'predefined_habit1', 'custom_habit1', 'predefined_habit2', 'custom_habit2') 

    def __str__(self):
        habit1 = self.predefined_habit1.name if self.predefined_habit1 else self.custom_habit1
        habit2 = self.predefined_habit2.name if self.predefined_habit2 else self.custom_habit2
        return f'{self.user.username} - {habit1} & {habit2}'