from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4

class UserRole(models.TextChoices):
    HOST = 'host'
    GUEST = 'guest'
    ADMIN = 'admin'

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    email = models.EmailField(unique=True, null=False)
    password_hash = models.CharField(max_length=128, null=False)
    phone_number = models.CharField(max_length=15, null=True)
    role = models.CharField(max_length=10, choices=UserRole.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.username}, {self.email}"

class Conversation(models.Model):

    conversation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}, participants: {[user.username for user in self.participants.all()] }"

class Message(models.Model):
 
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} sender: {self.sender_id.username}, conversation: {self.conversation.conversation_id}"