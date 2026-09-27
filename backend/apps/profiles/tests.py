"""
Tests for Profile API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from apps.skills.models import Category, Skill
from .models import UserSkill, Experience, Education, Certificate, Portfolio


class UserSkillAPITest(TestCase):
    """Tests for UserSkill CRUD."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_email_verified=True,
        )
        self.category = Category.objects.create(name='Web Development')
        self.skill = Skill.objects.create(name='Django', category=self.category)
        self.client.force_authenticate(self.user)

    def test_create_user_skill(self):
        response = self.client.post(
            reverse('profiles:my-skill-list'),
            {'skill': self.skill.id, 'proficiency': 'advanced', 'years_experience': 3},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_skill_rejected(self):
        UserSkill.objects.create(user=self.user, skill=self.skill)
        response = self.client.post(
            reverse('profiles:my-skill-list'),
            {'skill': self.skill.id, 'proficiency': 'beginner'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_own_skills(self):
        UserSkill.objects.create(user=self.user, skill=self.skill, proficiency='expert')
        response = self.client.get(reverse('profiles:my-skill-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExperienceAPITest(TestCase):
    """Tests for Experience CRUD."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_email_verified=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_experience(self):
        response = self.client.post(
            reverse('profiles:my-experience-list'),
            {
                'title': 'Software Engineer',
                'company': 'Google',
                'start_date': '2020-01-01',
                'is_current': True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_date_range(self):
        response = self.client.post(
            reverse('profiles:my-experience-list'),
            {
                'title': 'Dev', 'company': 'Corp',
                'start_date': '2023-01-01', 'end_date': '2022-01-01',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(TestCase):
    """Tests for public profile viewing."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_email_verified=True,
        )
        self.other = User.objects.create_user(
            email='other@test.com', password='TestPass123!',
            first_name='Other', last_name='User', is_email_verified=True,
        )
        self.client.force_authenticate(self.user)

    def test_view_profile(self):
        response = self.client.get(
            reverse('profiles:profile-detail', kwargs={'pk': self.other.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'other@test.com')

    def test_profile_list(self):
        response = self.client.get(reverse('profiles:profile-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
