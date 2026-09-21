"""
Tests for Review API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from apps.hiring.models import HireRequest
from .models import Review


class ReviewAPITest(TestCase):
    """Tests for Review CRUD."""

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
        self.hire_request = HireRequest.objects.create(
            client=self.user_client,
            provider=self.user_provider,
            title='Test Job',
            description='Description',
            status=HireRequest.Status.COMPLETED,
        )

    def test_create_review(self):
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('reviews:review-list'),
            {
                'reviewee': self.user_provider.id,
                'hire_request': self.hire_request.id,
                'rating': 5,
                'comment': 'Excellent work!',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_review_self(self):
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('reviews:review-list'),
            {
                'reviewee': self.user_client.id,
                'hire_request': self.hire_request.id,
                'rating': 5,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_review_pending_request(self):
        pending_hire = HireRequest.objects.create(
            client=self.user_client,
            provider=self.user_provider,
            title='Pending', description='Pending',
            status=HireRequest.Status.PENDING,
        )
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('reviews:review-list'),
            {
                'reviewee': self.user_provider.id,
                'hire_request': pending_hire.id,
                'rating': 3,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_reviews_by_reviewee(self):
        Review.objects.create(
            reviewer=self.user_client,
            reviewee=self.user_provider,
            hire_request=self.hire_request,
            rating=4,
        )
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.get(
            reverse('reviews:review-list'),
            {'reviewee': self.user_provider.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_duplicate_review_rejected(self):
        Review.objects.create(
            reviewer=self.user_client,
            reviewee=self.user_provider,
            hire_request=self.hire_request,
            rating=4,
        )
        self.client_api.force_authenticate(self.user_client)
        response = self.client_api.post(
            reverse('reviews:review-list'),
            {
                'reviewee': self.user_provider.id,
                'hire_request': self.hire_request.id,
                'rating': 5,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
