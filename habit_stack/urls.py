from django.urls import path
from .views import (
    HabitStackingListView,
    HabitStackingDetailView,
    HabitStackingLogListView, 
    HabitStackingLogEditView,
    HabitExtendView,
    FeedView,
    ShareMilestonePostView
)  

urlpatterns = [
    path('habit-stacking/', HabitStackingListView.as_view()),
    path('habit-stacking/<int:pk>/', HabitStackingDetailView.as_view()),
    path('habit-stacking-logs/', HabitStackingLogListView.as_view()),
    path('habit-stacking-logs/<int:pk>/', HabitStackingLogEditView.as_view()),
    path('habit-stacking/<int:pk>/extend/', HabitExtendView.as_view()),
    path('milestone-posts/<int:pk>/share/', ShareMilestonePostView.as_view()),
    path('feed/', FeedView.as_view()),
]