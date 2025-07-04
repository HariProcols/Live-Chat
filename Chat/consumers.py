import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_room"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send previous messages to the newly connected user
        messages = await self.get_last_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'username': msg.username,
                'message': msg.message
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        username = data['username']
        message = data['message']

        # Save the message to the database
        await self.save_message(username, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        username = event['username']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message
        }))

    @sync_to_async
    def get_last_messages(self):
        return Message.objects.order_by('-timestamp')[:20][::-1]  # Last 20 messages, oldest first

    @sync_to_async
    def save_message(self, username, message):
        Message.objects.create(username=username, message=message)
