from django.contrib import admin
from .models import(
    HabitStacking, 
    PredefinedHabit, 
    HabitStackingLog,  
    Milestone) 

admin.site.register(HabitStacking)
admin.site.register(PredefinedHabit)
admin.site.register(HabitStackingLog)
admin.site.register(Milestone)