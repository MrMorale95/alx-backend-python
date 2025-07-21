# chats/permissions.py
from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to allow access only to participants of a conversation.
    """

    def has_permission(self, request, view):
        # For list or create actions - allow authenticated users
        # More complex logic can be added as needed
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # obj here could be a Conversation or Message instance

        if hasattr(obj, 'participants'):
            # obj is Conversation, check user in participants
            return request.user in obj.participants.all()

        elif hasattr(obj, 'conversation'):
            # obj is Message, check user in conversation participants
            return request.user in obj.conversation.participants.all()

        return False
