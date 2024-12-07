from django.urls import path
from .views import HabitStackingListView, HabitStackingDetailView

urlpatterns = [
    path('habit-stacking/', HabitStackingListView.as_view()),
    path('habit-stacking/<int:pk>/', HabitStackingDetailView.as_view()),
]