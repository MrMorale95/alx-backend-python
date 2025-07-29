from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from .models import Message, Notification, MessageHistory, User

@receiver(post_save, sender=Message)
def send_notification_to_message_receiver(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(recipient=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if instance.pk:
        old_message = Message.objects.get(pk=instance.pk)
        if old_message.content != instance.content:
            # log message
            print(f"Message edited: {old_message.content} -> {instance.content}")
            MessageHistory.objects.create(
                edited=old_message.content,
                message=old_message,
                edited_by=instance.sender,
            )

@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    user_messages = Message.objects.filter(sender=instance)
    user_notifications = Notification.objects.filter(recipient=instance)
    user_message_history = MessageHistory.objects.filter(edited_by=instance)

    user_messages.delete()
    user_notifications.delete()
    user_message_history.delete()