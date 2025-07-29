from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to retrieve unread messages for a specific user.
    Uses .only() to fetch minimal required fields for optimization.
    """
    def for_user(self, user):
        return self.filter(receiver=user, read=False).only(
            "id", "sender", "content", "timestamp"
        )
