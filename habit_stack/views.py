from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .models import HabitStacking, HabitStackingLog, Milestone
from .serializers import (
    HabitStackingSerializer,
    HabitStackingLogSerializer,
    HabitStackingLogEditSerializer,
    HabitExtendSerializer)
from habit_api.permissions import IsAuthenticatedAndOwnerOrReadOnly
from django.utils import timezone
from datetime import timedelta


def calculate_streak(user, habit_stack):
    """
    Calculates the current streak for a specific habit stack.
    A streak consists of consecutive completed days without gaps.
    """
    logs = HabitStackingLog.objects.filter(
        user=user,
        habit_stack=habit_stack,
        completed=True
    ).order_by('-date')

    if not logs.exists():
        return 0

    current_streak = 1
    prev_date = logs[0].date

    for log in logs[1:]:
        if (prev_date - log.date).days == 1:
            current_streak += 1
        else:
            break

        prev_date = log.date

    return current_streak


class HabitStackingListView(generics.ListCreateAPIView):
    """
    Handles listing all habit stacks for the logged-in user
    and creating new ones.
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
        Creates a new habit stack for the logged-in user
        and automatically creates logs for the next 7 days.
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
        Ensures only habit stacks belonging to the
        logged-in user are accessible.
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
        return HabitStackingLog.objects.filter(
            user=self.request.user
            ).order_by('date')


class HabitStackingLogEditView(generics.UpdateAPIView):
    """
    Handles updating a specific habit log, marking it as completed.
    """
    serializer_class = HabitStackingLogEditSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Ensures only habit logs belonging to the logged-in user are accessible.
        """
        return HabitStackingLog.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        log = serializer.save()
        milestone_message = None
        streak_message = None

        if log.completed:
            # Recalculate streaks dynamically
            current_streak = calculate_streak(log.user, log.habit_stack)

            if current_streak >= 2:
                streak_message = f"You're on a {current_streak}-day streak! Keep it up!"

            # Calculate total completions and check for milestones
            total_completions = HabitStackingLog.objects.filter(
                habit_stack=log.habit_stack,
                user=log.user,
                completed=True
            ).count()

            if total_completions % 5 == 0:
                milestone = Milestone.objects.create(
                    habit_stack=log.habit_stack,
                    date_achieved=log.date,
                    description=f"Milestone achieved: {total_completions} completions!"
                )
                milestone_message = milestone.description

            log.streak_message = streak_message
            log.save()

        self.milestone_message = milestone_message
        self.streak_message = streak_message

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data['milestone_message'] = getattr(self, 'milestone_message', None)
        response.data['streak_message'] = getattr(self, 'streak_message', None)
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

        # Default extension to 7 days, but allow 14 days if specified
        extension_days = int(request.data.get('extension_days', 7))
        if extension_days not in [7, 14]:
            return Response({"success": False, "error": "Invalid extension period"}, status=400)

        try:
            # Get the last log date (or default to today)
            last_log = HabitStackingLog.objects.filter(habit_stack=habit_stack).order_by('-date').first()
            new_start_date = last_log.date if last_log else timezone.now().date()

            # Calculate new active_until
            new_active_until = new_start_date + timedelta(days=extension_days)

            # Extend and create logs only for missing dates
            habit_stack.active_until = new_active_until
            habit_stack.save()

            new_logs = []
            for i in range(extension_days):
                log_date = new_start_date + timedelta(days=i + 1)

                # Check if the log already exists
                if not HabitStackingLog.objects.filter(habit_stack=habit_stack, date=log_date).exists():
                    new_logs.append(HabitStackingLog(
                        habit_stack=habit_stack, user=habit_stack.user, date=log_date, completed=False
                    ))

            HabitStackingLog.objects.bulk_create(new_logs)

            return Response({
                "success": True,
                "message": f"Habit extended by {extension_days} days.",
                "id": habit_stack.id,
                "active_until": habit_stack.active_until,
            }, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)


class HabitProgressView(generics.RetrieveAPIView):
    """
    Displays progress for each habit stack, including current streak and milestones.
    """
    serializer_class = HabitStackingSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        """
        Ensure the view only retrieves habit stacks belonging to the logged-in user.
        """
        return HabitStacking.objects.filter(user=self.request.user)

    def get_object(self):
        """
        Retrieves a single habit stack belonging to the logged-in user.
        """
        habit_stack_id = self.kwargs.get('pk')
        return get_object_or_404(HabitStacking, user=self.request.user, id=habit_stack_id)

    def retrieve(self, request, *args, **kwargs):
        """
        Override the retrieve method to calculate streak details dynamically.
        """
        habit_stack = self.get_object()

        # Calculate streak
        current_streak = calculate_streak(request.user, habit_stack)

        # Calculate total completions and milestones
        logs = HabitStackingLog.objects.filter(
            habit_stack=habit_stack,
            user=request.user
        ).order_by('-date')

        milestones = Milestone.objects.filter(habit_stack=habit_stack).values('date_achieved', 'description')

        progress_data = {
            "habit_stack": HabitStackingSerializer(habit_stack).data,
            "current_streak": current_streak,
            "total_completions": logs.filter(completed=True).count(),
            "milestones": list(milestones),
        }

        return Response(progress_data, status=status.HTTP_200_OK)
