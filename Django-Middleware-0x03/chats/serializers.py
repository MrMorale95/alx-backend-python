from rest_framework import serializers
from .models import User, Conversation, Message

# -------------------
# User Serializer
# -------------------
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    id = serializers.UUIDField(source='user_id', read_only=True)  # Match model

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'bio', 'phone_number',
            'is_online', 'last_seen', 'password'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

# -------------------
# Message Serializer
# -------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    id = serializers.UUIDField(source='message_id', read_only=True)
    message_body = serializers.CharField(max_length=1000)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sender', 'sent_at']

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value

# -------------------
# Conversation Serializer (Read + Write)
# -------------------
class ConversationSerializer(serializers.ModelSerializer):
    # Write: accept participant IDs
    participants_input = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='participants'
    )

    # Read: show full participant details
    participants = UserSerializer(many=True, read_only=True)

    messages = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()
    id = serializers.UUIDField(source='conversation_id', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id',
            'participants',          # read-only
            'participants_input',    # write-only
            'participant_count',
            'created_at',
            'messages'
        ]
        read_only_fields = ['id', 'created_at']

    def get_messages(self, obj):
        messages = obj.messages.order_by('-sent_at')[:50]
        return MessageSerializer(messages, many=True, context=self.context).data

    def get_participant_count(self, obj):
        return obj.participants.count()

    def validate(self, data):
        participants = data.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError(
                {"participants": "Conversation must have at least 2 participants"}
            )
        return data

# -------------------
# Conversation Create Serializer (Write-Only Simplified)
# -------------------
class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    id = serializers.UUIDField(source='conversation_id', read_only=True)

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
    