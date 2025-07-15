from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    # Using SerializerMethodField for computed field
    full_name = serializers.SerializerMethodField()
    status = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                'full_name', 'status', 'bio', 'phone_number',
                'is_online', 'last_seen', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def get_full_name(self, obj):
        """SerializerMethodField example implementation"""
        return f"{obj.first_name} {obj.last_name}"

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=1000)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()  # Using SerializerMethodField for messages
    participant_count = serializers.SerializerMethodField()  # Another example

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participant_count', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

    def get_messages(self, obj):
        """Custom method for nested messages with pagination"""
        messages = obj.messages.order_by('-timestamp')[:50]  # Last 50 messages
        return MessageSerializer(messages, many=True, context=self.context).data

    def get_participant_count(self, obj):
        """Another SerializerMethodField example"""
        return obj.participants.count()

    def validate(self, data):
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError(
                {"participants": "Conversation must have at least 2 participants"}
            )
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
            raise serializers.ValidationError("At least 2 participants required")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate participants not allowed")
        return value