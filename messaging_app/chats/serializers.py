from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'bio', 'phone_number', 'is_online', 'last_seen']
        extra_kwargs = {
            'password': {'write_only': True}  # Never include password in responses
        }


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)  # Nested user data (read-only)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']  # Auto-set fields


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)  # Nested messages
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at', 'messages']
        read_only_fields = ['id', 'created_at', 'messages']

    # Custom handling for participant IDs during creation
    def create(self, validated_data):
        participants_data = self.initial_data.get('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants_data)
        return conversation


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True  # Only for input, not output
    )
    
    class Meta:
        model = Conversation
        fields = ['id', 'participants']
        read_only_fields = ['id']

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation