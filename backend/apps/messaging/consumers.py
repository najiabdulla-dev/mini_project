import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UserConsumer(AsyncWebsocketConsumer):
    """
    Consumer for user-specific real-time updates (messages, notifications).
    Connects to a personal channel group based on the user's ID.
    """
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f'user_{user.id}'

        # Join the personal group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            # Leave the personal group
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        # We don't currently expect incoming websocket messages from the client.
        # Sending is handled via REST POST, which broadcasts back here.
        pass

    # Custom event handler for new messages
    async def new_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'data': message
        }))

    # Custom event handler for new notifications
    async def new_notification(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': notification
        }))
