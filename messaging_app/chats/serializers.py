from rest_framework import serializers
from .models import User, Conversation, Message
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    # Adding SerializerMethodField example
    full_name = serializers.SerializerMethodField()
    # Adding CharField example
    status = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'status', 'bio', 'phone_number', 
            'is_online', 'last_seen', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_full_name(self, obj):
        """SerializerMethodField example"""
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        """ValidationError example"""
        if not value.endswith('@example.com'):
            raise ValidationError("Only example.com emails are allowed")
        return value

    def validate(self, data):
        """Complex validation example"""
        if len(data.get('password', '')) < 8:
            raise ValidationError({
                'password': "Password must be at least 8 characters long"
            })
        return data


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    # CharField with custom validation
    content = serializers.CharField(
        max_length=1000,
        error_messages={
            'max_length': "Message cannot exceed 1000 characters"
        }
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    # SerializerMethodField example
    participant_count = serializers.SerializerMethodField()
    # CharField example for custom output
    last_message_preview = serializers.CharField(
        source='get_last_message_preview',
        read_only=True
    )

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_count',
            'created_at', 'messages', 'last_message_preview'
        ]
        read_only_fields = ['id', 'created_at', 'messages']

    def get_participant_count(self, obj):
        """SerializerMethodField example"""
        return obj.participants.count()

    def validate(self, data):
        """ValidationError example for participants"""
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise ValidationError({
                'participants': "Conversation must have at least 2 participants"
            })
        return data


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True
    )
    # CharField example for custom input
    conversation_title = serializers.CharField(
        write_only=True,
        required=False,
        max_length=100
    )

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'conversation_title']
        read_only_fields = ['id']

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation