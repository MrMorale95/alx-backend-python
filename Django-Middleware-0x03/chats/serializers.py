from rest_framework import serializers
from .models import User, Message, Conversation
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('username', 'email','password')
        extra_kwargs = {'email':{"required":True}}
        
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
      

class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    
    class Meta:
        model = User
        fields = ["id", 'email', 'first_name', 'last_name',]
        read_only_fields = ['id']
        
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ["message_id", 'sender', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    
    class Meta:
        model = Conversation
        fields = ["conversation_id", 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
        
    def get_messages(self,obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data
    
    def validate(self, data):
        if not data.get("participants"):
            raise serializers.ValidationError("Conversation must have at least one participant")
        return data