from django.contrib import admin
from .models import(
    HabitStacking, 
    PredefinedHabit, 
    HabitStackingLog, 
    StreakAndMilestoneTracker, 
    MilestonePost) 

admin.site.register(HabitStacking)
admin.site.register(PredefinedHabit)
admin.site.register(HabitStackingLog)
admin.site.register(StreakAndMilestoneTracker)
admin.site.register(MilestonePost)