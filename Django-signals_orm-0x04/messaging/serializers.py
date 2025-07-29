from rest_framework import serializers
from .models import User, Message, Notification, MessageHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = ['id']
class RecursiveMessageSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'replies']
        read_only_fields = ['id', 'timestamp']

    def get_replies(self, obj):
        replies = obj.replies.all()
        if replies:
            return RecursiveMessageSerializer(replies, many=True).data
        return []

class MessageSerializer(serializers.ModelSerializer):
    replies = RecursiveMessageSerializer(many=True, read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'parent_message', 'replies']
        read_only_fields = ['id', 'timestamp']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'message', 'seen', 'timestamp']

class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['id', 'edited', 'message', 'edited_at', 'edited_by']
        read_only_fields = ['id', 'edited', 'message', 'edited_at', 'edited_by']