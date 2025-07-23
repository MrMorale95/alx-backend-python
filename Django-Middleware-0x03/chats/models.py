from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

class Conversation(models.Model):
  conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  participants = models.ManyToManyField(User, related_name="conversations")
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"Message {self.id} from {self.sender} in {self.conversation}"
    