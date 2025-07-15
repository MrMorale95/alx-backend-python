from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
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
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        # Explicit use of ValidationError
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email is already in use.")
        return value

    def validate(self, data):
        # Another explicit ValidationError
        if len(data.get('password', '')) < 8:
            raise ValidationError({
                'password': "Password must be at least 8 characters long"
            })
        return data


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    content = serializers.CharField(max_length=1000)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']

    def validate_content(self, value):
        # ValidationError for message content
        if len(value.strip()) == 0:
            raise ValidationError("Message content cannot be empty")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participant_count',
            'created_at', 'messages'
        ]
        read_only_fields = ['id', 'created_at', 'messages']

    def get_participant_count(self, obj):
        return obj.participants.count()

    def validate(self, data):
        # ValidationError for participant count
        participants = self.initial_data.get('participants', [])
        if len(participants) < 2:
            raise ValidationError(
                "Conversation must have at least 2 participants"
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
        # ValidationError for duplicate participants
        if len(value) != len(set(value)):
            raise ValidationError("Duplicate participants are not allowed")
        return value