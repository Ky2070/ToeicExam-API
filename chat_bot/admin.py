from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at', 'user']
    search_fields = ['content', 'user__username', 'user__email']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
