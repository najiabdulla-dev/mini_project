"""
Tests for Skill and Category API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from .models import Category, Skill


class CategoryAPITest(TestCase):
    """Tests for Category CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_verified=True,
        )
        self.admin = User.objects.create_user(
            email='admin@test.com', password='TestPass123!',
            first_name='Admin', last_name='User', is_verified=True, is_admin=True,
        )
        self.category = Category.objects.create(
            name='Web Development', icon='🌐', description='Web dev skills',
        )

    def test_list_categories(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('skills:category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category_admin_only(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('skills:category-list'),
            {'name': 'Design', 'icon': '🎨'},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('skills:category-list'),
            {'name': 'Design', 'icon': '🎨'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search_categories(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('skills:category-list'), {'search': 'Web'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SkillAPITest(TestCase):
    """Tests for Skill CRUD operations."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_verified=True,
        )
        self.admin = User.objects.create_user(
            email='admin@test.com', password='TestPass123!',
            first_name='Admin', last_name='User', is_verified=True, is_admin=True,
        )
        self.category = Category.objects.create(name='Web Development')
        self.skill = Skill.objects.create(
            name='Django', category=self.category, description='Python web framework',
        )

    def test_list_skills(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('skills:skill-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_skills_by_category(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('skills:skill-list'), {'category': self.category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_skill_admin_only(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('skills:skill-list'),
            {'name': 'Flask', 'category': self.category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_skill_as_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse('skills:skill-list'),
            {'name': 'Flask', 'category': self.category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_skill(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('skills:skill-detail', kwargs={'pk': self.skill.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Django')
