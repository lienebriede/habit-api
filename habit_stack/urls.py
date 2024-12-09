from django.urls import path
from .views import HabitStackingListView, HabitStackingDetailView, HabitStackingLogListView 

urlpatterns = [
    path('habit-stacking/', HabitStackingListView.as_view()),
    path('habit-stacking/<int:pk>/', HabitStackingDetailView.as_view()),
    path('habit-stacking-logs/', HabitStackingLogListView.as_view()),
]