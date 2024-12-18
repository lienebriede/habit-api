from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import(
    HabitStacking, 
    PredefinedHabit, 
    HabitStackingLog, 
    StreakAndMilestoneTracker) 
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
            goal='DAILY'
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
            goal='NO_GOAL'
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
            'goal': 'DAILY',
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_stack_validation_error(self):
        """Test validation error when creating a habit stack with invalid data."""
        self.client.login(username='Maija', password='001')
        data = {
            'predefined_habit1': self.habit1.id,
            'custom_habit1': 'Invalid custom habit'
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_stack_unauthenticated(self):
        """Test if unauthenticated users are forbidden from creating a habit stack."""
        data = {
            'predefined_habit1': self.habit1.id,
            'predefined_habit2': self.habit2.id,
            'goal': 'DAILY'
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
            goal='DAILY'
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
            goal='NO_GOAL'
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
        """Test if a user is forbidden from accessing another user's habit stack."""
        self.client.login(username='Janis', password='002')
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit_stack(self):
        """Test if an authenticated user can update their habit stack."""
        self.client.login(username='Maija', password='001')
        data = {
            'custom_habit1': 'Updated habit1',
            'predefined_habit2': self.habit2.id,
            'goal': 'NO_GOAL'
        }
        response = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_habit_stack_forbidden(self):
        """Test if a user is forbidden from updating another user's habit stack."""
        self.client.login(username='Janis', password='002')
        data = {'goal': 'NO_GOAL'}
        response = self.client.put(f'/habit-stacking/{self.habit_stack1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit_stack(self):
        """Test if an authenticated user can delete their habit stack."""
        self.client.login(username='Maija', password='001')
        response = self.client.delete(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_habit_stack_forbidden(self):
        """Test if a user is forbidden from deleting another user's habit stack."""
        self.client.login(username='Janis', password='002')
        response = self.client.delete(f'/habit-stacking/{self.habit_stack1.id}/')
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
            goal='DAILY'
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
            goal='NO_GOAL'
        )
    
        # Create logs for habit_stack1 for 7 days
        self._create_auto_logs(self.habit_stack1)

    def _create_auto_logs(self, habit_stack):
        """Helper function to create 7 habit stacking logs for the given habit stack."""
        for i in range(7):
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=habit_stack.user,
                date=(timezone.now().date() + timedelta(days=i)),
                completed=False
            )
    def test_habit_stacking_log_list_authenticated(self):
        """Test if an authenticated user can view their own habit stacking logs."""
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
            expected_date = (timezone.now().date() + timedelta(days=i)).isoformat()
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
            goal='DAILY'
        )

        # Create logs for habit_stack1 for 7 days
        self._create_auto_logs(self.habit_stack1)

    def _create_auto_logs(self, habit_stack):
        """Helper function to create 7 habit stacking logs for the given habit stack."""
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
        response = self.client.patch(f'/habit-stacking-logs/{log.id}/', {'completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(HabitStackingLog.objects.get(id=log.id).completed)

    def test_habit_stacking_log_update_undo(self):
        """Test if a user can undo completion of a habit stacking log."""
        self.client.login(username='Maija', password='001')
        log = HabitStackingLog.objects.filter(user=self.user1).first()
        log.completed = True
        log.save()
        response = self.client.patch(f'/habit-stacking-logs/{log.id}/', {'completed': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(HabitStackingLog.objects.get(id=log.id).completed)

class StreakAndMilestoneTrackerTests(APITestCase):

    def setUp(self):
        """Set up test data for Streak and Milestone Tracker tests."""
        # Create user and predefined habit
        self.user = User.objects.create_user(username='Maija', password='001')
        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')

        # Create habit stack
        self.habit_stack = HabitStacking.objects.create(
            user=self.user,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
            goal='DAILY'
        )

        # Create a streak and milestone tracker for the habit stack
        self.tracker = StreakAndMilestoneTracker.objects.create(
            user=self.user,
            habit_stack=self.habit_stack
        )

    def test_update_streak_and_completions_on_success(self):
        """Test if the streak and total completions update correctly when a habit is successfully completed."""
        completed_today = True

        initial_streak = self.tracker.current_streak
        initial_completions = self.tracker.total_completions
        initial_longest_streak = self.tracker.longest_streak

        milestone_message = self.tracker.update_streak_and_completions(completed_today)
        self.tracker.refresh_from_db()

        self.assertEqual(self.tracker.current_streak, initial_streak + 1)
        self.assertEqual(self.tracker.total_completions, initial_completions + 1)
        self.assertEqual(self.tracker.longest_streak, max(initial_longest_streak, self.tracker.current_streak))
        self.assertIsNone(milestone_message)

    def test_streak_reset_on_incompletion(self):
        """Test if the streak resets to 0 when a habit is not completed."""
        self.tracker.current_streak = 5
        self.tracker.save()

        self.tracker.update_streak_and_completions(completed_today=False)
        self.tracker.refresh_from_db()

        self.assertEqual(self.tracker.current_streak, 0)

    def test_milestone_achieved(self):
        """Test if a milestone message is returned when a milestone is reached."""
        self.tracker.total_completions = 4
        self.tracker.save()

        milestone_message = self.tracker.update_streak_and_completions(completed_today=True)
        self.tracker.refresh_from_db()

        self.assertEqual(self.tracker.total_completions, 5)
        self.assertIn("Congratulations! You've reached 5 completions!", milestone_message)
        self.assertIn(str(timezone.now().date()), self.tracker.milestone_dates)

    def test_multiple_milestones(self):
        """Test if multiple milestones can be achieved and recorded."""
        self.tracker.total_completions = 48
        self.tracker.save()

        self.tracker.update_streak_and_completions(completed_today=True)
        self.tracker.update_streak_and_completions(completed_today=True)
        self.tracker.refresh_from_db()

        self.assertEqual(self.tracker.total_completions, 50)
        self.assertIn(str(timezone.now().date()), self.tracker.milestone_dates)

    def test_no_future_logs_allowed(self):
        """Test that future logs are not allowed when updating streaks and completions."""
        HabitStackingLog.objects.create(
            habit_stack=self.habit_stack,
            user=self.user,
            date=timezone.now().date() + timedelta(days=1),
            completed=False
        )

        milestone_message = self.tracker.update_streak_and_completions(completed_today=False)
        self.tracker.refresh_from_db()

        self.assertEqual(self.tracker.current_streak, 0)
        self.assertEqual(self.tracker.total_completions, 0)
        self.assertIsNone(milestone_message)

class HabitStackingExtendAndLogTests(APITestCase):

    def setUp(self):
        """Set up test data for HabitStacking extend and log view tests."""
        
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

        self.habit1 = PredefinedHabit.objects.create(name='Habit 1')
        self.habit2 = PredefinedHabit.objects.create(name='Habit 2')

        self.habit_stack1 = HabitStacking.objects.create(
            user=self.user1,
            predefined_habit1=self.habit1,
            predefined_habit2=self.habit2,
            goal='DAILY'
        )
        self.habit_stack2 = HabitStacking.objects.create(
            user=self.user2,
            predefined_habit1=self.habit1,
            custom_habit2='Custom Habit 2',
            goal='NO_GOAL'
        )
    
    def test_extend_habit_stack_success(self):
        """Test if the habit stack can be extended successfully by 7 days."""
        self.client.login(username='Maija', password='001')
        data = {'extension_days': 7}
        response = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/extend/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.habit_stack1.refresh_from_db()
        self.assertEqual(self.habit_stack1.active_until, (timezone.now().date() + timedelta(days=7)))
    
    def test_extend_habit_stack_unauthenticated(self):
        """Test if unauthenticated users are prevented from extending a habit stack."""
        data = {'extension_days': 7}
        response = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/extend/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extend_habit_stack_not_found(self):
        """Test if an invalid habit stack ID returns a not found error."""
        self.client.login(username='Maija', password='001')
        data = {'extension_days': 7}
        response = self.client.patch('/habit-stacking/9999/extend/', data, format='json')  # Invalid ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_habit_stacking_logs_updated_after_extend(self):
        """Test if new logs are created after extending the habit stack."""
        self.client.login(username='Maija', password='001')
        initial_log_count = HabitStackingLog.objects.count()
        data = {'extension_days': 7}
        response = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/extend/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_log_count = HabitStackingLog.objects.count()
        self.assertEqual(new_log_count, initial_log_count + 7)

    def test_habit_stacking_logs_no_duplicates(self):
        """Test if duplicate logs are not created when extending the habit stack multiple times.
        First extend for 7 days, then for 14 and expect 14 days in total."""
        self.client.login(username='Maija', password='001')
        initial_log_count = HabitStackingLog.objects.count()

        data = {'extension_days': 7}
        response1 = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/extend/', data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.habit_stack1.refresh_from_db()
        new_log_count_1 = HabitStackingLog.objects.count()
        self.assertEqual(new_log_count_1, initial_log_count + 7)

        data = {'extension_days': 14}
        response2 = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/extend/', data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.habit_stack1.refresh_from_db()
        new_log_count_2 = HabitStackingLog.objects.count()

        self.assertEqual(new_log_count_2, initial_log_count + 14)
        log_dates = HabitStackingLog.objects.filter(habit_stack=self.habit_stack1).values_list('date', flat=True)
        self.assertEqual(len(log_dates), len(set(log_dates)))
