from rest_framework import generics
from .models import HabitStacking
from .serializers import HabitStackingSerializer
from habit_api.permissions import IsAuthenticatedAndOwnerOrReadOnly

# HabitStacking list and create view
class HabitStackingListView(generics.ListCreateAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return HabitStacking.objects.filter(user=self.request.user)

    # Ensures it's tied to the logged-in user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# HabitStacking retrieve, update, and delete view
class HabitStackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return HabitStacking.objects.all()

    def perform_update(self, serializer):
        # Ensures partial update works correctly
        serializer.save(user=self.request.user)