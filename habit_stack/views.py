from rest_framework import generics, status
from rest_framework.response import Response
from .models import HabitStacking, HabitStackingLog, StreakAndMilestoneTracker, MilestonePost
from .serializers import (
    HabitStackingSerializer, 
    HabitStackingLogSerializer,
    HabitStackingLogEditSerializer,
    HabitExtendSerializer,
    MilestonePostSerializer) 
from habit_api.permissions import IsAuthenticatedAndOwnerOrReadOnly
from django.utils import timezone
from datetime import timedelta

class HabitStackingListView(generics.ListCreateAPIView):
    """
    Handles listing all habit stacks for the logged-in user and creating new ones.
    """
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Retrieves habit stacks belonging to the logged-in user.
        """
        return HabitStacking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Creates a new habit stack for the logged-in user and automatically creates
        logs for the next 7 days.
        """
        habit_stack = serializer.save(user=self.request.user)

        for i in range(7):
            log_date = timezone.now().date() + timedelta(days=i)
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=self.request.user,
                date=log_date,
                completed=False
            )
  
class HabitStackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, or deleting a specific habit stack.
    """
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Ensures only habit stacks belonging to the logged-in user are accessible.
        """
        return HabitStacking.objects.all()

    def perform_update(self, serializer):
        """
        Ensures the habit stack is updated for the logged-in user.
        """
        instance = self.get_object()
        serializer.save(user=self.request.user)

class HabitStackingLogListView(generics.ListAPIView):
    """
    Lists all habit logs for the logged-in user, ordered by date.
    """
    serializer_class = HabitStackingLogSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Retrieves habit logs belonging to the logged-in user.
        """
        return HabitStackingLog.objects.filter(user=self.request.user).order_by('date')

class HabitStackingLogEditView(generics.UpdateAPIView):
    """
    Handles updating a specific habit log, marking it as completed.
    Updates streaks and milestones for the associated habit stack.
    """
    serializer_class = HabitStackingLogEditSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Ensures only habit logs belonging to the logged-in user are accessible.
        """
        return HabitStackingLog.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Update the streak and milestone tracker when a log is marked as completed.
        """
        log = serializer.save()
        milestone_message = None
        streak_message = None

        if log.completed:
            tracker, created = StreakAndMilestoneTracker.objects.get_or_create(
                user=self.request.user,
                habit_stack=log.habit_stack
            )

            milestone_message = tracker.update_streak_and_completions(completed_today=True)

            if tracker.current_streak >= 2:
                streak_message = f"You're on a {tracker.current_streak}-day streak! Keep it up!"

        self.milestone_message = milestone_message
        self.streak_message = streak_message

    def update(self, request, *args, **kwargs):
        """
        Add streak and milestone messages to the response.
        """
        response = super().update(request, *args, **kwargs)
        response.data['streak_message'] = getattr(self, 'streak_message', None)
        response.data['milestone_message'] = getattr(self, 'milestone_message', None)
        return response

class HabitExtendView(generics.UpdateAPIView):
    """
    Extends a habit stack's active period.
    """
    queryset = HabitStacking.objects.all()
    serializer_class = HabitExtendSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Restrict the queryset to habits owned by the authenticated user.
        """
        return HabitStacking.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Override the update method to handle extending the habit stack.
        """
        habit_stack = self.get_object()

        # Get the extension days from the request data (default to 7 days)
        extension_days = request.data.get('extension_days', 7)

        try:
            # Extend the habit stack using the updated method
            habit_stack.extend_habit(int(extension_days))
            habit_stack.save()

            # Create the response with updated data
            response_data = {
                "success": True,
                "message": f"Habit successfully extended by {extension_days} days.",
                "id": habit_stack.id,
                "active_until": habit_stack.active_until,
            }
            return Response(response_data, status=200)

        except Exception as e:
            # Return an error response if something goes wrong
            return Response({"success": False, "error": str(e)}, status=400)

class FeedView(generics.ListAPIView):
    """
    API view to list all milestone posts in the feed.
    """
    queryset = MilestonePost.objects.filter(shared_on_feed=True).order_by('-created_at')
    serializer_class = MilestonePostSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

class ShareMilestonePostView(generics.UpdateAPIView):
    """
    Endpoint for sharing milestone posts to the feed.
    """
    queryset = MilestonePost.objects.all()
    serializer_class = MilestonePostSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        """
        Handle the user's confirmation to share a milestone post.
        """
        milestone_post = self.get_object()
        if milestone_post.user != request.user:
            return Response(
                {"error": "You do not have permission to share this milestone post."},
                status=status.HTTP_403_FORBIDDEN,
            )
        milestone_post.shared_on_feed = True
        milestone_post.save()
        return Response(
            {
                "success": True,
                "message": "Milestone post shared successfully.",
                "id": milestone_post.id,
            },
            status=status.HTTP_200_OK,
        )