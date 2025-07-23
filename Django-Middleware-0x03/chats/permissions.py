from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Only authenticated users allowed
    - Only participants of the conversation can view, send, update, or delete messages
    """

    def has_permission(self, request, view):
        # Allow access only if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for GET, POST, PUT, PATCH, DELETE.
        """
        user = request.user

        # Allow only participants for any object-level action
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            if hasattr(obj, 'participants'):
                # obj is a Conversation
                return user in obj.participants.all()
            elif hasattr(obj, 'conversation'):
                # obj is a Message
                return user in obj.conversation.participants.all()
            return False

        # For safe methods not listed above, allow by default
        return True
