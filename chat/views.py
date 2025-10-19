# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatInputSerializer, ChatMessageSerializer
from .ai_service import ai_service

class ChatSessionListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all chat sessions for the user"""
        sessions = ChatSession.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new chat session"""
        session = ChatSession.objects.create(user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, session_id):
        """Get specific chat session with messages"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)
    
    def delete(self, request, session_id):
        """Delete a chat session"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChatMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Send a message and get AI response"""
        serializer = ChatInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        session_id = serializer.validated_data.get('session_id')
        
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            session=session,
            message=message,
            is_user=True
        )
        
        # Get AI response
        ai_response = ai_service.get_ai_response(message)
        
        # Save AI response
        ai_message = ChatMessage.objects.create(
            session=session,
            message=ai_response,
            is_user=False
        )
        
        # Update session timestamp
        session.save()
        
        # Return both messages
        response_data = {
            'session_id': session.id,
            'user_message': ChatMessageSerializer(user_message).data,
            'ai_message': ChatMessageSerializer(ai_message).data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

class StreamChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Stream AI response (for real-time streaming in future)"""
        serializer = ChatInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        
        # For now, return immediate response (can be enhanced for real streaming)
        ai_response = ai_service.get_ai_response(message)
        
        return Response({
            'response': ai_response,
            'stream_complete': True
        })