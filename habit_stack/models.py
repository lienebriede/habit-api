from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

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
    active_until = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'predefined_habit1', 'custom_habit1', 'predefined_habit2', 'custom_habit2') 

    def extend_habit(self, days):
        """
        Extend the active period of the habit stack and ensure no duplicate logs are created.
        """
        old_active_until = self.active_until
        self.active_until = timezone.now().date() + timedelta(days=days)
        self.goal = 'DAILY'
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

        return {"success": True, "message": "Habit stack extended successfully."}

    def __str__(self):
        habit1 = self.predefined_habit1.name if self.predefined_habit1 else self.custom_habit1
        habit2 = self.predefined_habit2.name if self.predefined_habit2 else self.custom_habit2
        return f'{self.user.username} - {habit1} & {habit2}'


class HabitStackingLog(models.Model):
    habit_stack = models.ForeignKey(HabitStacking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit_stack', 'user', 'date')

    def __str__(self):
        return f'{self.habit_stack} - {self.date} - Completed: {self.completed}'


class StreakAndMilestoneTracker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit_stack = models.ForeignKey(HabitStacking, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_completions = models.IntegerField(default=0)
    milestone_dates = models.JSONField(default=list)

    def update_streak_and_completions(self, completed_today):
        if self.habit_stack.habitstackinglog_set.filter(date__gt=timezone.now().date()).exists():
            return None
        
        milestone_achieved = None
        if completed_today:
            self.current_streak += 1
            self.total_completions += 1

            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak

            milestone_achieved = self.check_milestone()
        else:
            self.current_streak = 0

        self.save()
        return milestone_achieved

    def check_milestone(self):
        milestone_thresholds = {5, 10, 20, 30, 40, 50}
        if self.total_completions in milestone_thresholds:
            milestone_message = f"Congratulations! You've reached {self.total_completions} completions!"
            self.milestone_dates.append(str(timezone.now().date()))
            self.save()
            return milestone_message
        return None

    def __str__(self):
        return f'{self.user.username} - {self.habit_stack}: Current Streak: {self.current_streak}, Longest: {self.longest_streak}, Total: {self.total_completions}'
