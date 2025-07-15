from django.db import models
from django.contrib.auth.models import AbstractUser


class user(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    # profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.username


class conversation(models.Model):
    participants = models.ManyToManyField(user, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class message(models.Model):
    conversation = models.ForeignKey(conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(user, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} in Conversation {self.conversation.id}"
