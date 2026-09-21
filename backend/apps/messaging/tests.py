"""
Tests for Messaging API endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.authentication.models import User
from .models import Message


class MessageAPITest(TestCase):
    """Tests for Message API."""

    def setUp(self):
        self.client_api = APIClient()
        self.sender = User.objects.create_user(
            email='sender@test.com', password='TestPass123!',
            first_name='Sender', last_name='User', is_verified=True,
        )
        self.receiver = User.objects.create_user(
            email='receiver@test.com', password='TestPass123!',
            first_name='Receiver', last_name='User', is_verified=True,
        )

    def test_send_message(self):
        self.client_api.force_authenticate(self.sender)
        response = self.client_api.post(
            reverse('messaging:message-list'),
            {'receiver': self.receiver.id, 'content': 'Hello!'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_message_self(self):
        self.client_api.force_authenticate(self.sender)
        response = self.client_api.post(
            reverse('messaging:message-list'),
            {'receiver': self.sender.id, 'content': 'Self message'},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_messages(self):
        Message.objects.create(
            sender=self.sender, receiver=self.receiver, content='Hi',
        )
        self.client_api.force_authenticate(self.sender)
        response = self.client_api.get(reverse('messaging:message-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_read(self):
        msg = Message.objects.create(
            sender=self.sender, receiver=self.receiver, content='Read me',
        )
        self.client_api.force_authenticate(self.receiver)
        response = self.client_api.post(
            reverse('messaging:message-mark-read', kwargs={'pk': msg.pk}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

    def test_conversations(self):
        Message.objects.create(
            sender=self.sender, receiver=self.receiver, content='Hey',
        )
        self.client_api.force_authenticate(self.sender)
        response = self.client_api.get(
            reverse('messaging:message-conversations'),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
