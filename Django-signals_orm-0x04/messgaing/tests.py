from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Message, Notification


class MessagingSignalsTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='alice', password='password')
        self.receiver = User.objects.create_user(username='bob', password='password')

    def test_notification_created_on_message(self):
        """
        When a Message is created, a Notification for the receiver is automatically created.
        """
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )
        notification = Notification.objects.filter(user=self.receiver, message=message)
        self.assertTrue(notification.exists(), "Notification was not created for receiver")

    def test_notification_links_correctly(self):
        """
        The Notification links correctly to the User and Message.
        """
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="How are you?"
        )
        notification = Notification.objects.get(user=self.receiver, message=message)
        self.assertEqual(notification.message.content, "How are you?")
        self.assertEqual(notification.user.username, "bob")
        self.assertFalse(notification.is_read, "New notifications should default to unread")

    def test_multiple_messages_create_multiple_notifications(self):
        """
        Multiple messages should create one notification each.
        """
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content=f"Message {i}"
            )
        self.assertEqual(Notification.objects.filter(user=self.receiver).count(), 3)


class MessagingAdminTest(TestCase):
    """
    Simple smoke test to confirm admin pages for Message and Notification work.
    """
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

    def test_admin_message_changelist(self):
        response = self.client.get(reverse('admin:messaging_message_change'))
