from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import HabitStacking, PredefinedHabit, HabitStackingLog
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


class HabitStackingListViewTests(APITestCase):
    def setUp(self):
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
        # Test if authenticated user can view their own habit stacks
        self.client.login(username='Maija', password='001')
        response = self.client.get('/habit-stacking/')
        # Response OK and Maijas stack is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_habit_stacking_list_view_unauthenticated(self):
        # Test if unauthenticated user gets 403 Forbidden
        response = self.client.get('/habit-stacking/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_habit_stack(self):
        self.client.login(username='Maija', password='001')
        
        # Test if can make a new habit stack
        data = {
            'custom_habit1': 'New habit1',
            'custom_habit2': 'New habit2',
            'goal': 'DAILY',
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_stack_validation_error(self):
        self.client.login(username='Maija', password='001')

        # Try to create a habit stack with invalid data and get error
        data = {
            'predefined_habit1': self.habit1.id,
            'custom_habit1': 'Invalid custom habit'
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_stack_unauthenticated(self):
        # Test trying to create a habit stack without authentication
        data = {
            'predefined_habit1': self.habit1.id,
            'predefined_habit2': self.habit2.id,
            'goal': 'DAILY'
        }
        response = self.client.post('/habit-stacking/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class HabitStackingDetailViewTests(APITestCase):
    def setUp(self):
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
        # Test if authenticated user can view their habit stack details
        self.client.login(username='Maija', password='001')
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_stacking_detail_view_unauthenticated(self):
        # Test if unauthenticated user gets 403 Forbidden
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_stacking_detail_view_forbidden(self):
        # Test if user tries to access another user's habit stack
        self.client.login(username='Janis', password='002')
        response = self.client.get(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_habit_stack(self):
        # Test updating a habit stack
        self.client.login(username='Maija', password='001')
        
        data = {
            'custom_habit1': 'Updated habit1',
            'predefined_habit2': self.habit2.id,
            'goal': 'NO_GOAL'
        }

        response = self.client.patch(f'/habit-stacking/{self.habit_stack1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_habit_stack_forbidden(self):
        # Test trying to update someone else's habit stack
        self.client.login(username='Janis', password='002')
        data = {'goal': 'NO_GOAL'}
        response = self.client.put(f'/habit-stacking/{self.habit_stack1.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_habit_stack(self):
        # Test deleting a habit stack
        self.client.login(username='Maija', password='001')
        response = self.client.delete(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_habit_stack_forbidden(self):
        # Test trying to delete someone else's habit stack
        self.client.login(username='Janis', password='002')
        response = self.client.delete(f'/habit-stacking/{self.habit_stack1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class HabitStackingLogListViewTests(APITestCase):

    def setUp(self):
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
        # Automatically create 7 habit stacking logs for the next 7 days
        for i in range(7):
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=habit_stack.user,
                date=(timezone.now().date() + timedelta(days=i)),
                completed=False
            )
    def test_habit_stacking_log_list_authenticated(self):
        # Test if authenticated user can view their own habit stacking logs
        self.client.login(username='Maija', password='001')
        response = self.client.get('/habit-stacking-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)

    def test_habit_stacking_log_list_unauthenticated(self):
        # Test if unauthenticated user gets 403 Forbidden
        response = self.client.get('/habit-stacking-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_habit_stacking_log_auto_creation_7_days(self):
        # Test that 7 habit stacking logs are created
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
        for i in range(7):
            HabitStackingLog.objects.create(
                habit_stack=habit_stack,
                user=habit_stack.user,
                date=(timezone.now().date() + timedelta(days=i)),
                completed=False
            )

    def test_habit_stacking_log_update_complete(self):
        self.client.login(username='Maija', password='001')

        # Test if can update the completion
        log = HabitStackingLog.objects.filter(user=self.user1).first()
        response = self.client.patch(f'/habit-stacking-logs/{log.id}/', {'completed': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(HabitStackingLog.objects.get(id=log.id).completed)

    def test_habit_stacking_log_update_undo(self):
        self.client.login(username='Maija', password='001')

        # Test if can undo completion
        log = HabitStackingLog.objects.filter(user=self.user1).first()
        log.completed = True
        log.save()
        response = self.client.patch(f'/habit-stacking-logs/{log.id}/', {'completed': False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(HabitStackingLog.objects.get(id=log.id).completed)