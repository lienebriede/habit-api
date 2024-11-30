from django.db import models
from django.contrib.auth.models import User

class HabitStacking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit1 = models.CharField(max_length=255)
    habit2 = models.CharField(max_length=255)
    
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
        unique_together = ('user', 'habit1', 'habit2', 'goal')

    def __str__(self):
        return f'{self.user.username} - {self.habit1} & {self.habit2}'

    def save(self, *args, **kwargs):
        # Ensure that the habit stack is unique for the user
        if HabitStacking.objects.filter(user=self.user, habit1=self.habit1, habit2=self.habit2, goal=self.goal).exists():
            raise ValueError('This habit stack already exists for the user')
        super().save(*args, **kwargs)
