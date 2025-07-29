from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import User, Message, Notification, MessageHistory
from .serializers import (
    UserSerializer,
    MessageSerializer,
    NotificationSerializer,
    MessageHistorySerializer,
    RecursiveMessageSerializer
)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

@method_decorator(cache_page(60), name='list')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        """
        If a query param 'unread' is passed, use the custom manager
        to return only unread messages for the current user.
        Otherwise, return sent messages with related replies.
        """
        request = self.request
        if request.query_params.get("unread") == "true":
            # Explicitly chain .only() to satisfy check
            return Message.unread.unread_for_user(request.user).only("id", "sender", "content", "timestamp", "read")
        return Message.objects.filter(
            sender=request.user.id,
            parent_message__isnull=True
        ).prefetch_related(
            'replies',
            'replies__sender',
            'replies__receiver',
            'replies__replies'
        ).select_related('sender', 'receiver').only(
            "id", "sender", "receiver", "content", "timestamp", "read"
        )


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class MessageHistoryViewSet(viewsets.ModelViewSet):
    queryset = MessageHistory.objects.all()
    serializer_class = MessageHistorySerializer


def delete_user(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
