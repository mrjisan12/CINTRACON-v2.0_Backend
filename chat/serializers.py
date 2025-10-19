# chat/serializers.py
from rest_framework import serializers
from .models import ChatSession, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message', 'is_user', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'created_at', 'updated_at', 'messages']

class ChatInputSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)
    session_id = serializers.IntegerField(required=False, allow_null=True)