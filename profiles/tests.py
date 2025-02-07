from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Profile


class ProfileTests(APITestCase):
    def setUp(self):
        """Set up test users before each test."""
        self.user1 = User.objects.create_user(username='Maija', password='001')
        self.user2 = User.objects.create_user(username='Janis', password='002')

    def test_profile_created_on_user_creation(self):
        """Test that a profile is automatically created when a user registers."""
        self.assertTrue(Profile.objects.filter(user=self.user1).exists())
        self.assertTrue(Profile.objects.filter(user=self.user2).exists())

    def test_user_can_retrieve_own_profile(self):
        """Test that a user can fetch their own profile."""
        self.client.login(username='Maija', password='001')
        response = self.client.get(f'/profiles/{self.user1.profile.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user1.username)

    def test_user_cannot_access_other_profiles(self):
        """Test that a user cannot fetch another user's profile."""
        self.client.login(username='Maija', password='001')
        response = self.client.get(f'/profiles/{self.user2.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_profile(self):
        """Test that a user can update their own profile."""
        self.client.login(username='Janis', password='002')
        response = self.client.patch(
            f'/profiles/{self.user2.profile.id}/',
            {'name': 'Janis Updated'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user2.profile.refresh_from_db()
        self.assertEqual(self.user2.profile.name, 'Janis Updated')

    def test_user_cannot_update_other_profiles(self):
        """Test that a user cannot update another user's profile."""
        self.client.login(username='Maija', password='001')
        response = self.client.patch(
            f'/profiles/{self.user2.profile.id}/',
            {'name': 'Janis'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.user2.profile.refresh_from_db()
        self.assertNotEqual(self.user2.profile.name, 'Janis')
