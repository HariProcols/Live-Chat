from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'has_file', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'content')
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
        return '[No Message]'
    content_preview.short_description = 'Message Preview'

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
