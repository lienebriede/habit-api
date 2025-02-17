from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import (
    HabitStacking, 
    PredefinedHabit, 
    HabitStackingLog,
    Milestone)
from .views import calculate_streak
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


class HabitStackingListViewTests(APITestCase):
    def setUp(self):
        """Set up test data for HabitStacking list view tests."""
        # Create users
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

        # Create predefined habits
        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')
        self.habit3 = PredefinedHabit.objects.create(name='Habit 3')
        self.habit4 = PredefinedHabit.objects.create(name='Habit 4')

        # Create habit stacks for each user
        self.habit_stack1 = HabitStacking.objects.create(
            user=self.user1,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
        )

    def test_habit_stacking_list_view_authenticated(self):
        """Test if an authenticated user can view their own habit stacks."""
        self.client.login(username='Maija', password='001')
        response = self.client.get('/habit-stacking/')
        # Response OK and Maijas stack is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_habit_stacking_list_view_unauthenticated(self):
        """Test if an unauthenticated user gets a 403 Forbidden response."""
        response = self.client.get('/habit-stacking/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_habit_stack(self):
        """Test if an authenticated user can create a new habit stack."""
        self.client.login(username='Maija', password='001')
        data = {
            'custom_habit1': 'New habit1',
            'custom_habit2': 'New habit2',
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_stack_validation_error(self):
        """
        Test validation error when 
        creating a habit stack with invalid data.
        """
        self.client.login(username='Maija', password='001')
        data = {
            'predefined_habit1': self.habit1.id,
            'custom_habit1': 'Invalid custom habit'
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_stack_unauthenticated(self):
        """
        Test if unauthenticated users are forbidden 
        from creating a habit stack.
        """
        data = {
            'predefined_habit1': self.habit1.id,
            'predefined_habit2': self.habit2.id,
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitStackingDetailViewTests(APITestCase):
    def setUp(self):
        """Set up test data for HabitStacking detail view tests."""
        # Create users
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

        # Create predefined habits
        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')

        # Create habit stacks for each user
        self.habit_stack1 = HabitStacking.objects.create(
            user=self.user1,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
        )

    def test_habit_stacking_detail_view_authenticated(self):
        """Test if an authenticated user can view their habit stack details."""
        self.client.login(username='Maija', password='001')
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_stacking_detail_view_unauthenticated(self):
        """Test if an unauthenticated user gets a 403 Forbidden response."""
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_stacking_detail_view_forbidden(self):
        """
        Test if a user is forbidden from accessing another
        user's habit stack.
        """
        self.client.login(username='Janis', password='002')
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit_stack(self):
        """Test if an authenticated user can update their habit stack."""
        self.client.login(username='Maija', password='001')
        data = {
            'custom_habit1': 'Updated habit1',
            'predefined_habit2': self.habit2.id,
        }
        response = self.client.patch(
            f'/habit-stacking/{self.habit_stack1.id}/',
            data, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_habit_stack_forbidden(self):
        """Test if a user is forbidden from updating 
        another user's habit stack.
        """
        self.client.login(username='Janis', password='002')
        data = {'custom_habit1': 'Updated habit1'}
        response = self.client.put(
            f'/habit-stacking/{self.habit_stack1.id}/',
            data, format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit_stack(self):
        """Test if an authenticated user can delete their habit stack."""
        self.client.login(username='Maija', password='001')
        response = self.client.delete(
            f'/habit-stacking/{self.habit_stack1.id}/'
            )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_habit_stack_forbidden(self):
        """
        Test if a user is forbidden from deleting
        another user's habit stack.
        """
        self.client.login(username='Janis', password='002')
        response = self.client.delete(
            f'/habit-stacking/{self.habit_stack1.id}/'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class HabitStackingLogListViewTests(APITestCase):

    def setUp(self):
        """Set up test data for HabitStacking log list view tests."""
        # Create users
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

        # Create predefined habits
        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')
        self.habit3 = PredefinedHabit.objects.create(name='Habit 3')
        self.habit4 = PredefinedHabit.objects.create(name='Habit 4')

        # Create habit stacks for each user
        self.habit_stack1 = HabitStacking.objects.create(
            user=self.user1,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
        )
    
        # Create logs for habit_stack1 for 7 days
        self._create_auto_logs(self.habit_stack1)

    def _create_auto_logs(self, habit_stack):
        """
        Helper function to create 7 habit stacking logs
        for the given habit stack.
        """
        for i in range(7):
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=habit_stack.user,
                date=(timezone.now().date() + timedelta(days=i)),
                completed=False
            )

    def test_habit_stacking_log_list_authenticated(self):
        """
        Test if an authenticated user can view
        their own habit stacking logs.
        """
        self.client.login(username='Maija', password='001')
        response = self.client.get('/habit-stacking-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_habit_stacking_log_list_unauthenticated(self):
        """Test if an unauthenticated user gets a 403 Forbidden response."""
        response = self.client.get('/habit-stacking-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_stacking_log_auto_creation_7_days(self):
        """Test that 7 habit stacking logs are created for 7 days."""
        self.client.login(username='Maija', password='001')
        response = self.client.get('/habit-stacking-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)
        
        # Test the logs are created for the next 7 days, 'completed' is False
        for i, log in enumerate(response.data):
            expected_date = (
                timezone.now().date() + timedelta(days=i)
                ).isoformat()
            self.assertEqual(log["date"], expected_date)
            self.assertFalse(log["completed"])
            

class HabitStackingLogEditViewTests(APITestCase):

    def setUp(self):
        """Set up test data for HabitStacking log edit view tests."""
        # Create user
        self.user1 = User.objects.create_user(username='Maija', password='001')

        # Create predefined habits and habit stack
        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')

        self.habit_stack1 = HabitStacking.objects.create(
            user=self.user1,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
        )

        # Create logs for habit_stack1 for 7 days
        self._create_auto_logs(self.habit_stack1)

    def _create_auto_logs(self, habit_stack):
        """
        Helper function to create 7 habit stacking
        logs for the given habit stack.
        """
        for i in range(7):
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=habit_stack.user,
                date=(timezone.now().date() + timedelta(days=i)),
                completed=False
            )

    def test_habit_stacking_log_update_complete(self):
        """Test if a user can mark a habit stacking log as completed."""
        self.client.login(username='Maija', password='001')
        log = HabitStackingLog.objects.filter(user=self.user1).first()
        response = self.client.patch(
            f'/habit-stacking-logs/{log.id}/', {'completed': True}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(HabitStackingLog.objects.get(id=log.id).completed)

    def test_habit_stacking_log_update_undo(self):
        """Test if a user can undo completion of a habit stacking log."""
        self.client.login(username='Maija', password='001')
        log = HabitStackingLog.objects.filter(user=self.user1).first()
        log.completed = True
        log.save()
        response = self.client.patch(
            f'/habit-stacking-logs/{log.id}/', {'completed': False}
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(HabitStackingLog.objects.get(id=log.id).completed)


class StreakAndMilestoneTests(APITestCase):

    def setUp(self):
        """Setup users and a habit stack."""
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

        self.habit_stack = HabitStacking.objects.create(
            user=self.user1, custom_habit1="Daily Reading"
            )

    def test_streak_increases_correctly(self):
        """ Test that the streak increases correctly
        when logs are consecutive.
        """
        today = timezone.now().date()

        # Create logs for 3 consecutive days
        for i in range(3):
            HabitStackingLog.objects.create(
                habit_stack=self.habit_stack,
                user=self.user1, date=today - timedelta(days=i), completed=True
                )

        # Calculate streak
        current_streak = calculate_streak(self.user1, self.habit_stack)

        self.assertEqual(current_streak, 3, "Current streak should be 3")

    def test_streak_resets_after_missed_day(self):
        """Test that the streak resets if a day is missed."""
        today = timezone.now().date()

        # Completed today and 2 days ago (missed yesterday)
        HabitStackingLog.objects.create(
            habit_stack=self.habit_stack,
            user=self.user1,
            date=today, completed=True
            )
        HabitStackingLog.objects.create(
            habit_stack=self.habit_stack,
            user=self.user1, date=today - timedelta(days=2), completed=True
            )

        # Calculate streak
        current_streak = calculate_streak(self.user1, self.habit_stack)

        self.assertEqual(
            current_streak, 1,
            "Current streak should reset to 1 after a missed day"
            )

    def test_milestone_at_5_completions(self):
        """Test that a milestone is created after 5 completed logs."""
        today = timezone.now().date()

        # Complete 5 logs
        for i in range(5):
            HabitStackingLog.objects.create(
                habit_stack=self.habit_stack,
                user=self.user1, date=today - timedelta(days=i), completed=True
                )

        total_completions = HabitStackingLog.objects.filter(
            habit_stack=self.habit_stack,
            user=self.user1, completed=True
            ).count()

        # Check for milestone
        if total_completions == 5:
            Milestone.objects.create(
                habit_stack=self.habit_stack,
                date_achieved=today,
                description="Milestone achieved: 5 completions!"
                )

        self.assertEqual(Milestone.objects.count(), 1)
        self.assertEqual(
            Milestone.objects.first().description,
            "Milestone achieved: 5 completions!"
            )

    def test_milestone_at_10_completions(self):
        """Test that a milestone is created after 10 completed logs."""
        today = timezone.now().date()

        # Complete 10 logs
        for i in range(10):
            HabitStackingLog.objects.create(habit_stack=self.habit_stack, user=self.user1, date=today - timedelta(days=i), completed=True)

        total_completions = HabitStackingLog.objects.filter(habit_stack=self.habit_stack, user=self.user1, completed=True).count()

        # Check for milestone
        if total_completions == 10:
            Milestone.objects.create(habit_stack=self.habit_stack, date_achieved=today, description="Milestone achieved: 10 completions!")

        self.assertEqual(Milestone.objects.count(), 1, "There should be only 1 milestone created at 10 completions")
        self.assertEqual(Milestone.objects.first().description, "Milestone achieved: 10 completions!")

    def test_progress_view(self):
        """ Test that the progress view returns the correct streak and milestone data."""
        today = timezone.now().date()

        # Complete 3 consecutive logs
        for i in range(3):
            HabitStackingLog.objects.create(habit_stack=self.habit_stack, user=self.user1, date=today - timedelta(days=i), completed=True)

        self.client.login(username='Maija', password='001')
        response = self.client.get(f'/habit-stacking/{self.habit_stack.id}/progress/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        progress_data = response.json()
        self.assertEqual(progress_data['current_streak'], 3)
        self.assertEqual(progress_data['total_completions'], 3)
        self.assertEqual(len(progress_data['milestones']), 0, "No milestones should be created yet")