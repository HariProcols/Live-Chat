from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Message

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token

def index(request):
    messages = Message.objects.order_by('timestamp')  # oldest first
    return render(request, 'Chat/home.html', {
        'csrf_token': get_token(request),
        'messages': messages
    })
@require_POST
def upload(request):
    file = request.FILES.get('file')
    username = request.POST.get('username')

    if file and username:
        user, _ = User.objects.get_or_create(username=username)

        # Save the uploaded message with file
        message = Message.objects.create(user=user, file=file)
        file_url = message.file.url

        # Detect type
        is_image = message.is_image_file
        is_audio = message.is_audio_file

        # Send to WebSocket group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_room',
            {
                'type': 'chat_message',
                'username': username,
                'message': '',
                'file_url': file_url,
                'is_image': is_image,
                'is_audio': is_audio,
            }
        )

        return JsonResponse({'status': 'ok', 'url': file_url})

    return JsonResponse({'status': 'error', 'message': 'Missing file or username'})
