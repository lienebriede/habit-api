from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PredefinedHabit(models.Model):
    """
    Represents a predefined habit that can be part of a habit stack.
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class HabitStacking(models.Model):
    """
    Represents a stack of habits for a user,
    which can include predefined or custom habits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predefined_habit1 = models.ForeignKey(
        PredefinedHabit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='habit1_set'
        )
    custom_habit1 = models.CharField(max_length=255, blank=True)
    predefined_habit2 = models.ForeignKey(
        PredefinedHabit,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='habit2_set'
        )
    custom_habit2 = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active_until = models.DateField(default=timezone.now)

    class Meta:
        unique_together = (
            'user', 'predefined_habit1',
            'custom_habit1', 'predefined_habit2',
            'custom_habit2')

    def extend_habit(self, days):
        """
        Extends the active period of the habit stack by the specified number
        of days. Creates new logs for the additional days
        without duplicating existing logs.
        """
        old_active_until = self.active_until
        self.active_until = timezone.now().date() + timedelta(days=days)
        self.save()

        # Calculate new dates
        new_dates = [
            old_active_until + timedelta(days=i)
            for i in range(1, (self.active_until - old_active_until).days + 1)
        ]

        # Exclude dates that already have logs
        existing_dates = HabitStackingLog.objects.filter(
            habit_stack=self,
            user=self.user,
            date__in=new_dates
        ).values_list('date', flat=True)

        logs_to_create = [
            HabitStackingLog(
                habit_stack=self,
                user=self.user,
                date=log_date,
                completed=False
            )
            for log_date in new_dates if log_date not in existing_dates
        ]

        # Create logs only for new dates
        HabitStackingLog.objects.bulk_create(logs_to_create)

        return {
            "success": True,
            "message": "Habit stack extended successfully."
            }

    def __str__(self):
        habit1 = (self.predefined_habit1.name
                  if self.predefined_habit1
                  else self.custom_habit1)
        habit2 = (self.predefined_habit2.name
                  if self.predefined_habit2
                  else self.custom_habit2)
        return f'{self.user.username} - {habit1} & {habit2}'


class HabitStackingLog(models.Model):
    """
    Represents a daily log entry for a habit stack,
    tracking completion status for a specific date.
    """
    habit_stack = models.ForeignKey(HabitStacking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit_stack', 'user', 'date')

    def __str__(self):
        return (
            f"{self.habit_stack} - {self.date} - "
            f"Completed: {self.completed}"
            )


class Milestone(models.Model):
    """
    Represents a milestone achieved for a habit stack.
    """
    habit_stack = models.ForeignKey(HabitStacking, on_delete=models.CASCADE)
    date_achieved = models.DateField()
    description = models.CharField(max_length=255)

    def __str__(self):
        return (
            f"Milestone for {self.habit_stack}: {self.description} "
            f"on {self.date_achieved}"
        )
