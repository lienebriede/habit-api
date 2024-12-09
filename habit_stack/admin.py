from django.contrib import admin
from .models import HabitStacking, PredefinedHabit, HabitStackingLog

admin.site.register(HabitStacking)
admin.site.register(PredefinedHabit)
admin.site.register(HabitStackingLog)
