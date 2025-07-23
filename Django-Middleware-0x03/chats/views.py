from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, filters, generics, permissions, status
from .models import User, Conversation, Message
from .serializers import  ConversationSerializer,MessageSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsParticipantOfConversation
from .pagination import MessagePagination
from .filters import MessageFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes= [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        participants_ids = self.request.data.get('participants', [])
        if not participants_ids:
            raise serializer.ValidationError("Participants field is required")
        conversation = serializer.save()
        conversation.participants.set(participants_ids)
        conversation.save()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']


    def get_queryset(self):
        conversation_pk = self.kwargs['conversation_pk']
        return Message.objects.filter(conversation__pk=conversation_pk, conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation_pk = self.kwargs['conversation_pk']
        conversation = Conversation.objects.get(pk=conversation_pk)
        serializer.save(sender=self.request.user, conversation=conversation)


class RegisterViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request,*args, **kwargs):
          serializer = self.get_serializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          user = serializer.save()
          
          refresh = RefreshToken.for_user(user)
          token_data = {
              'refresh_token': str(refresh),
              'access_token': str(refresh.access_token) 
          }
          
          return Response({
              'user':serializer.data,
              'token': token_data
          }, status=status.HTTP_201_CREATED)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST) 