"""
Tests for Hiring API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from .models import HireRequest


class HireRequestAPITest(TestCase):
    """Tests for HireRequest CRUD and status transitions."""

    def setUp(self):
        self.client_api = APIClient()
        self.user_client = User.objects.create_user(
            email='client@test.com', password='TestPass123!',
            first_name='Client', last_name='User', is_verified=True,
        )
        self.user_provider = User.objects.create_user(
            email='provider@test.com', password='TestPass123!',
            first_name='Provider', last_name='User', is_verified=True,
        )

    def test_create_hire_request(self):
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('hiring:hire-request-list'),
            {
                'provider': self.user_provider.id,
                'title': 'Build a website',
                'description': 'I need a landing page built.',
                'budget': '500.00',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_hire_self(self):
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('hiring:hire-request-list'),
            {
                'provider': self.user_client.id,
                'title': 'Self hire',
                'description': 'Testing',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_provider_accept(self):
        self.client_api.force_authenticate(self.user_client)
        create_resp = self.client_api.post(
            reverse('hiring:hire-request-list'),
            {
                'provider': self.user_provider.id,
                'title': 'Test job',
                'description': 'Description',
            },
        )
        hire_id = create_resp.data['id']

        self.client_api.force_authenticate(self.user_provider)
        response = self.client_api.post(
            reverse('hiring:hire-request-update-status', kwargs={'pk': hire_id}),
            {'action': 'accept'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'accepted')

    def test_provider_reject(self):
        hire = HireRequest.objects.create(
            client=self.user_client,
            provider=self.user_provider,
            title='Test', description='Test',
        )
        self.client_api.force_authenticate(self.user_provider)
        response = self.client_api.post(
            reverse('hiring:hire-request-update-status', kwargs={'pk': hire.pk}),
            {'action': 'reject', 'rejection_reason': 'Too busy'},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['status'], 'rejected')

    def test_invalid_transition(self):
        hire = HireRequest.objects.create(
            client=self.user_client,
            provider=self.user_provider,
            title='Test', description='Test',
            status=HireRequest.Status.COMPLETED,
        )
        self.client_api.force_authenticate(self.user_provider)
        response = self.client_api.post(
            reverse('hiring:hire-request-update-status', kwargs={'pk': hire.pk}),
            {'action': 'accept'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_own_requests(self):
        HireRequest.objects.create(
            client=self.user_client,
            provider=self.user_provider,
            title='Test', description='Test',
        )
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.get(reverse('hiring:hire-request-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
