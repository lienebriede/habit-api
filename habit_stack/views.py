from rest_framework import generics
from .models import HabitStacking, HabitStackingLog
from .serializers import HabitStackingSerializer, HabitStackingLogSerializer
from habit_api.permissions import IsAuthenticatedAndOwnerOrReadOnly
from django.utils import timezone
from datetime import timedelta

# HabitStacking list and create view
class HabitStackingListView(generics.ListCreateAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return HabitStacking.objects.filter(user=self.request.user)

    # Ensures it's tied to the logged-in user
    def perform_create(self, serializer):
        habit_stack = serializer.save(user=self.request.user)

        # Automatically create logs for the next 7 days if 'DAILY'
        if habit_stack.goal == 'DAILY':
            for i in range(7):
                log_date = timezone.now().date() + timedelta(days=i)
                HabitStackingLog.objects.create(
                    habit_stack=habit_stack,
                    user=self.request.user,
                    date=log_date,
                    completed=False
                )
  
# HabitStacking retrieve, update, and delete view
class HabitStackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return HabitStacking.objects.all()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# HabitStackingLog list view
class HabitStackingLogListView(generics.ListAPIView):
    serializer_class = HabitStackingLogSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return HabitStackingLog.objects.filter(user=self.request.user).order_by('date')

    