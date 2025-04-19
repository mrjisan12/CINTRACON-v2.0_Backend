# serializers.py
from rest_framework import serializers
# from django.contrib.auth.models import User
from users.models import UserProfile
from django.contrib.auth import get_user_model 

# Get the custom user model
User = get_user_model()

# Student Profile Serializers for All Students API
class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    email = serializers.EmailField(source='user.email')
    total_post = serializers.SerializerMethodField()  # Key declaration
    profile_photo = serializers.SerializerMethodField() 

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'full_name',
            'email',
            'department',
            'semester',
            'batch_no',
            'points',
            'section',
            'profile_photo',
            'total_post',
            'facebook_link',
            'instagram_link',
            'linkedin_link'
        ]
    
    def get_profile_photo(self, obj):
        if obj.profile_photo:
            return str(obj.profile_photo)
        return None

    # Correctly indented method (NOT inside Meta class)
    def get_total_post(self, obj):
        """
        Calculate total posts for the user
        """
        # First try User->posts relationship
        if hasattr(obj.user, 'posts'):
            return obj.user.posts.count()
        
        # Then try UserProfile->posts relationship
        if hasattr(obj, 'posts'):
            return obj.posts.count()
            
        return 0  # Default if no relationship found