from rest_framework import generics, permissions
from .models import HabitStacking
from .serializers import HabitStackingSerializer


# HabitStacking list and create view
class HabitStackingListView(generics.ListCreateAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HabitStacking.objects.filter(user=self.request.user).order_by('id')

    # Ensures it's tied to the logged-in user
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# HabitStacking retrieve, update, and delete view
class HabitStackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitStackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HabitStacking.objects.filter(user=self.request.user).order_by('id')