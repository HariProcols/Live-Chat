# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "global_chat"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send previous messages
        messages = await self.get_message_history()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'username': msg.username,
                'message': msg.text
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data['username']
        message = data['message']

        # Save to DB
        await self.save_message(username, message)

        # Broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        Message.objects.create(username=username, text=message)

    @database_sync_to_async
    def get_message_history(self):
        return Message.objects.order_by('timestamp')
