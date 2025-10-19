# chat/urls.py
from django.urls import path
from .views import ChatSessionListView, ChatSessionDetailView, ChatMessageView, StreamChatView

urlpatterns = [
    path('sessions/', ChatSessionListView.as_view(), name='chat-sessions'),
    path('sessions/<int:session_id>/', ChatSessionDetailView.as_view(), name='chat-session-detail'),
    path('message/', ChatMessageView.as_view(), name='chat-message'),
    path('stream/', StreamChatView.as_view(), name='chat-stream'),
]

