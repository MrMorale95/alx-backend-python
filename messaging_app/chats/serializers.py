from rest_framework import serializers
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
            raise serializers.ValidationError("Message content cannot be empty")  # Explicit use
        return value

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)  # Nested messages

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise serializers.ValidationError(  # Explicit use
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
            raise serializers.ValidationError(  # Explicit use
                "At least 2 participants required"
            )
        if len(value) != len(set(value)):
            raise serializers.ValidationError(  # Explicit use
                "Duplicate participants not allowed"
            )
        return value