from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, ConversationCreateSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show conversations the user is part of
        return self.queryset.filter(participants=self.request.user)

    def get_serializer_class(self):
        # Use different serializer for creation
        if self.action == 'create':
            return ConversationCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        conversation = serializer.save()
        # Automatically add current user to participants
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data, context={
            'request': request,
            'conversation': conversation
        })

        if serializer.is_valid():
            serializer.save(
                sender=request.user,
                conversation=conversation
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show messages from conversations the user is part of
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')