"""
Tests for Notification API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from .models import Notification


class NotificationAPITest(TestCase):
    """Tests for Notification API."""

    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_email_verified=True,
        )
        self.notification = Notification.objects.create(
            user=self.user,
            title='New Hire Request',
            message='You received a new hire request.',
            type=Notification.Type.HIRE_REQUEST,
        )
        self.client_api.force_authenticate(self.user)

    def test_list_notifications(self):
        response = self.client_api.get(reverse('notifications:notification-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_read(self):
        response = self.client_api.post(
            reverse('notifications:notification-mark-read', kwargs={'pk': self.notification.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(
            user=self.user, title='Test2', message='Test2',
            type=Notification.Type.MESSAGE,
        )
        response = self.client_api.post(
            reverse('notifications:notification-mark-all-read'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Notification.objects.filter(user=self.user, is_read=False).count(), 0,
        )

    def test_unread_count(self):
        response = self.client_api.get(
            reverse('notifications:notification-unread-count'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)
