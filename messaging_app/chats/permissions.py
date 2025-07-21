from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Only authenticated users allowed
    - Only participants of the conversation can view/update/delete messages
    """

    def has_permission(self, request, view):
        # Allow access only if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission.
        obj can be Conversation or Message instance.
        """

        user = request.user

        if hasattr(obj, 'participants'):
            # obj is Conversation
            return user in obj.participants.all()

        elif hasattr(obj, 'conversation'):
            # obj is Message
            return user in obj.conversation.participants.all()

        return False
