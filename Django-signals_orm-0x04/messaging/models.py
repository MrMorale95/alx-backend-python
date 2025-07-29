from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    read = models.BooleanField(default=False)  # Added for unread tracking

    objects = models.Manager()                # Default manager
    unread = UnreadMessagesManager()  


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='message')
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class MessageHistory(models.Model):
    edited = models.TextField(null=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='edited_by')
