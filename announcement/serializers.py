from rest_framework import serializers
from .models import Announcement

class AnnouncementSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'created_at', 'created_by', 'created_by_name']
        read_only_fields = ['created_by', 'created_at']

class AnnouncementDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'description', 'created_at', 'created_by', 'created_by_name']
        read_only_fields = ['created_by', 'created_at']