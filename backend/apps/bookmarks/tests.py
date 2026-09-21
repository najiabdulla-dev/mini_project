"""
Tests for Bookmark API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from .models import Bookmark


class BookmarkAPITest(TestCase):
    """Tests for Bookmark API."""

    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            email='user@test.com', password='TestPass123!',
            first_name='Test', last_name='User', is_verified=True,
        )
        self.other = User.objects.create_user(
            email='other@test.com', password='TestPass123!',
            first_name='Other', last_name='User', is_verified=True,
        )
        self.client_api.force_authenticate(self.user)

    def test_create_bookmark(self):
        response = self.client_api.post(
            reverse('bookmarks:bookmark-list'),
            {'bookmarked_user': self.other.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_bookmark_self(self):
        response = self.client_api.post(
            reverse('bookmarks:bookmark-list'),
            {'bookmarked_user': self.user.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_bookmark_rejected(self):
        Bookmark.objects.create(user=self.user, bookmarked_user=self.other)
        response = self.client_api.post(
            reverse('bookmarks:bookmark-list'),
            {'bookmarked_user': self.other.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_bookmarks(self):
        Bookmark.objects.create(user=self.user, bookmarked_user=self.other)
        response = self.client_api.get(reverse('bookmarks:bookmark-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_toggle_bookmark(self):
        # Create
        response = self.client_api.post(
            reverse('bookmarks:bookmark-toggle'),
            {'bookmarked_user': self.other.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_bookmarked'])

        # Remove
        response = self.client_api.post(
            reverse('bookmarks:bookmark-toggle'),
            {'bookmarked_user': self.other.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_bookmarked'])

    def test_delete_bookmark(self):
        bookmark = Bookmark.objects.create(user=self.user, bookmarked_user=self.other)
        response = self.client_api.delete(
            reverse('bookmarks:bookmark-detail', kwargs={'pk': bookmark.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
