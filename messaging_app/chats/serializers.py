from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'bio', 'phone_number', 'is_online', 'last_seen']
        extra_kwargs = {'password': {'write_only': True}}


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=1000)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']

    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("Message cannot be empty")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

    def get_messages(self, obj):
        """Nested messages with pagination support"""
        messages = obj.messages.order_by('-timestamp')[:50]  # Last 50 messages
        return MessageSerializer(messages, many=True, context=self.context).data

    def validate(self, data):
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise ValidationError("Conversation must have at least 2 participants")
        return data


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants']
        read_only_fields = ['id']

    def validate_participants(self, value):
        if len(value) < 2:
            raise ValidationError("At least 2 participants required")
        return value