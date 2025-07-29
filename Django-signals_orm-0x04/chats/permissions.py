from rest_framework import permissions
from .models import Conversation, Message

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission class to check if the user is a participant of a conversation.

    This class ensures that the user requesting access to a specific conversation or
    message is authenticated and authorized by verifying their participation in the
    conversation. The permission can be used to restrict access to resources or
    functionalities based on the user's involvement in a conversation.

    Attributes:
        message : str
            A message returned when the user does not have sufficient permissions.
    """
    message = "You are not a participant in this conversation. Please join the conversation to access this resource."

    def has_permission(self, request, view):
        """
        Determines if a user has the necessary permissions to access or perform an action
        on a specific view or conversation. This includes checking for user authentication
        and verifying the user's participation in a conversation if applicable.

        Parameters:
            request: The request object containing user and request metadata.
            view: The view being accessed, which may contain details and keyword arguments
                  for permission checks.

        Returns:
            bool: True if the user is authorized to access the resource or perform the
            requested action, otherwise False.
        """
        if not request.user.is_authenticated:
            return False

        if view.detail:
            return True

        if 'conversation_pk' in view.kwargs:
            conversation_id = view.kwargs['conversation_pk']
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                return conversation.participants.filter(user_id=request.user.user_id).exists()
            except Conversation.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        Determines if the user has the necessary permissions to access a specific object.
        The object can either be a Conversation or a Message instance. The permission
        check ensures that the requesting user is authenticated and is a participant
        in the Conversation or its associated parent Conversation (for Messages).

        Parameters:
        request : HttpRequest
            The HTTP request object containing the user making the request.
        view : View
            The view being accessed.
        obj : Conversation or Message
            The specific instance of Conversation or Message being accessed.

        Returns:
        bool
            True if the user is authenticated and has access to the object, False otherwise.
        """
        NOT_SAFE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
        if not request.user.is_authenticated:
            return False

        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()

        if isinstance(obj, Message):
            isParticipant = obj.conversation.participants.filter(user_id=request.user.user_id).exists()

            if request.method in permissions.SAFE_METHODS:
                return isParticipant
            elif request.method in NOT_SAFE_METHODS:
                return isParticipant and obj.sender_id == request.user

        return False