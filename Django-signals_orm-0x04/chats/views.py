from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsParticipantOfConversation

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .pagination import StandardResultsSetPagination
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Conversation instances.

    This class provides standard CRUD functionality for the 'Conversation' model using
    Django REST Framework's ModelViewSet. It ensures that only authenticated users
    who are participants of a conversation can access it and perform relevant actions.

    Attributes:
        queryset: Queryset to fetch all conversations ordered by the creation date.
        serializer_class: Defines the serializer used for data serialization and deserialization.
        permission_classes: List of permissions applied to this ViewSet, ensuring user-specific
            access and participatory authorization.

    Methods:
        get_queryset():
            Implements custom queryset restriction to return only conversations
            the current user participates in.
        perform_create(serializer):
            Saves a new conversation instance and adds the authenticated user
            to its participants.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        """
        Restricts the returned conversations to those that the current
        authenticated user is a participant of.
        """
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(participants=self.request.user).order_by('-created_at')
        return Conversation.objects.none() # Return empty queryset if not authenticated


    def perform_create(self, serializer):
        conversation = serializer.save()
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)


    @action(detail=True, methods=['post'], url_path='send-message')
    def send_message(self, request, pk=None):
        try:
            conversation = self.get_object() # IsParticipantOfConversation will already check access here
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)

        if not conversation.participants.filter(user_id=request.user.user_id).exists():
            return Response({"detail": "You are not a participant in this conversation."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages in the application.

    This class provides functionality to manage messages, ensuring that users can only interact with
    messages in conversations they participate in. It applies strict permission checks to ensure privacy
    and integrity and allows users to create messages by automatically associating them with the current user.

    Attributes:
        queryset: A queryset of Message objects ordered by their sent_at date.
        serializer_class: The serializer class used to validate and serialize Message objects.
        permission_classes: A list of permission classes applied to this view set.
    """
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter


    def get_queryset(self):
        """
        Filters messages to ensure only messages from conversations the user participates in are visible.
        """
        if not self.request.user.is_authenticated:
            return Message.objects.none()

        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)
                if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
                    return Message.objects.none()
                return Message.objects.filter(conversation=conversation).order_by('sent_at')
            except Conversation.DoesNotExist:
                return Message.objects.none()

        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations).order_by('sent_at')


    def perform_create(self, serializer):
        """
        When creating a message via the MessageViewSet, automatically set the sender to the current user.
        The `conversation` field must be provided in the request data for direct message creation.
        """
        conversation_pk = self.kwargs.get('conversation_pk')
        if conversation_pk:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)
            except Conversation.DoesNotExist:
                raise serializer.ValidationError({"detail": "Parent conversation not found."})
        else:
            conversation_id = self.request.data.get('conversation')
            if not conversation_id:
                raise serializer.ValidationError({"conversation": "This field is required when creating a message directly."})
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
            except Conversation.DoesNotExist:
                raise serializer.ValidationError({"conversation": "Conversation not found."})

        if not conversation.participants.filter(user_id=self.request.user.user_id).exists():
            raise serializer.ValidationError({"detail": "You can only send messages to conversations you are a participant of."})

        serializer.save(sender_id=self.request.user, conversation=conversation)
