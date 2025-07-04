from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message
from channels.db import database_sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_room"  # match group in views.py upload()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data.get('username')
        message = data.get('message', '')
        typing = data.get('typing', None)

        if not username:
            return  # skip if username is missing

        # Handle typing indicator
        if typing is not None:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_status',
                    'username': username,
                    'typing': typing,
                }
            )
            return

        # Handle message
        if message:
            user = await self.get_or_create_user(username)
            msg = await self.create_message(user, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': user.username,
                    'message': msg.content,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event.get('message', ''),
            'file_url': event.get('file_url'),
            'is_image': event.get('is_image', False),
            'is_audio': event.get('is_audio', False),
        }))

    async def typing_status(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'typing': event['typing'],
        }))

    @database_sync_to_async
    def get_or_create_user(self, username):
        return User.objects.get_or_create(username=username)[0]

    @database_sync_to_async
    def create_message(self, user, content):
        return Message.objects.create(user=user, content=content)
