from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter, ConversationFilter
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, ConversationCreateSerializer, MessageSerializer, UserSerializer
from .permissions import IsParticipantOfConversation  # import the new permission
from django.contrib.auth.hashers import make_password
from rest_framework import generics
from rest_framework.permissions import AllowAny

class UserCreateView(generics.CreateAPIView):
    """
    API endpoint to create a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Ensure password is hashed
        password = serializer.validated_data.get('password')
        serializer.save(password=make_password(password))

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_message(self, request, pk=None):
        conversation = self.get_object()

        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not a participant in this conversation."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_pk = self.kwargs['conversation_pk']
        if not Conversation.objects.filter(pk=conversation_pk, participants=self.request.user).exists():
            return Message.objects.none()

        return Message.objects.filter(conversation_id=conversation_pk)
