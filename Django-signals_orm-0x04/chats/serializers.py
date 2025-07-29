from rest_framework import serializers
from .models import User, Conversation, Message, UserRole

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects
    This serializer is used to convert User model instance into JSON
    and vice versa.
    It includes all essential fields for user representation, excluding
    sensitive information like password_hash
    """
    role = serializers.ChoiceField(choices=UserRole.choices)

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']

    def create(self, validated_data):
        """
        Create and return a new `User` instance, given the validated data.
        We will manually set the password since AbstractUser handles hashing.
        """
        password = validated_data.pop('password_hash', None)
        user = User.objects.create_user(**validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """
        update and return an existing `User` instance, given the validated data.
        """
        password = validated_data.pop('password_hash', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for a Message object.

    This serializer is used to convert a Message model instance into JSON representation.
    It includes the sender's user_id and message content, along with the timestamp.
    """
    sender_email = serializers.CharField(source='sender_id.email', read_only=True)
    class Meta:
        model = Message
        fields = ['message_id', 'sender_id', 'sender_email', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at', 'sender_email']

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model, including nested messages.

    This serializer handles the Conversation model, showing its participants
    and a list of all messages associated with that conversation,
    ordered by the time they were sent
    """
    messages = MessageSerializer(many=True, read_only=True)
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    # last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']
        read_only_fields = ['conversation_id', 'created_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sender': last_message.sender.username,
                'timestamp': last_message.timestamp
            }
        return None