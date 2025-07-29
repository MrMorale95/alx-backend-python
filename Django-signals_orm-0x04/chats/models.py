from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4

class UserRole(models.TextChoices):
    """
    Enumeration of user roles for a system.

    This class represents different roles a user can have within a system,
    such as host, guest, or administrator. It uses Django's TextChoices to
    structure and manage these roles effectively.
    """
    HOST = 'host'
    GUEST = 'guest'
    ADMIN = 'admin'

class User(AbstractUser):
    """
    Represents a user in the system.

    This class is a custom user model extending from AbstractUser. It provides
    additional fields to store user-specific information such as unique identification,
    password hash, phone number, and role. The purpose of this model is to facilitate
    user management in an application with clearly defined roles and attributes.
    """
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
    """Represents a conversation model for capturing interactions between users.

    This class is used to define the structure and attributes of a conversation
    within a system. It allows the association of multiple participants (users)
    and tracks the creation time of the conversation. Primarily useful for systems
    handling messaging or collaborative discussions.

    Attributes:
        conversation_id: A unique identifier for the conversation.
        participants: A reference to the users participating in this conversation.
        created_at: The timestamp when the conversation was created.
    """
    conversation_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}, participants: {[user.username for user in self.participants.all()] }"

class Message(models.Model):
    """
    Represents a message in the system.

    This class is used to store and manage messages between users. Each message contains
    information about the sender, the message content, and the timestamp when the message
    was sent. Messages are uniquely identified by a UUID, ensuring global uniqueness.
    The sender of each message is linked to a user in the system.

    Attributes:
        message_id: A UUID that uniquely identifies the message.
        sender_id: A foreign key reference to the User model, representing the sender of
                   the message.
        message_body: The content of the message as a non-null text field.
        sent_at: A timestamp that indicates when the message was sent. It is automatically
                 set when the message is created.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} sender: {self.sender_id.username}, conversation: {self.conversation.conversation_id}"