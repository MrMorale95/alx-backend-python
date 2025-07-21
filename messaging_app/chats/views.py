from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter, ConversationFilter
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer
)
from .permissions import IsParticipantOfConversation  # Import custom permission


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet to list, retrieve, and create conversations.
    """
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        # Return conversations where the logged-in user is a participant
        return Conversation.objects.filter(participants=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        conversation = serializer.save()
        # Automatically add the requesting user to the participants
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_message(self, request, pk=None):
        """
        Custom endpoint: POST /conversations/<pk>/send_message/
        Allows a participant to send a message in the conversation.
        """
        conversation = self.get_object()

        # Check if user is part of the conversation
        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Attach conversation in context
        serializer = MessageSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(
                sender=request.user,
                conversation=conversation
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list messages from conversations the user is part of.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_pk = self.kwargs['conversation_pk']
        # Confirm that the user is a participant in the conversation
        if not Conversation.objects.filter(pk=conversation_pk, participants=self.request.user).exists():
            return Message.objects.none()  # no access

        # Return messages only for this conversation
        return Message.objects.filter(conversation_id=conversation_pk)
