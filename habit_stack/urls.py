from django.urls import path
from .views import (
    HabitStackingListView,
    HabitStackingDetailView,
    HabitStackingLogListView,
    HabitStackingLogEditView,
    HabitExtendView,
    HabitProgressView,
)

urlpatterns = [
    path('habit-stacking/', HabitStackingListView.as_view()),
    path('habit-stacking/<int:pk>/', HabitStackingDetailView.as_view()),
    path('habit-stacking/<int:pk>/extend/', HabitExtendView.as_view()),
    path('habit-stacking/<int:pk>/progress/', HabitProgressView.as_view()),
    path('habit-stacking-logs/', HabitStackingLogListView.as_view()),
    path('habit-stacking-logs/<int:pk>/', HabitStackingLogEditView.as_view()),
]
