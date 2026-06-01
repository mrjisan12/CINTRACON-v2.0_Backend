# serializers.py
import cloudinary.uploader
from rest_framework import serializers
from .models import *
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    profile_photo = serializers.CharField(source='profile.profile_photo.url', allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'profile_photo']



class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['reaction_type', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name')
    profile_photo = serializers.CharField(source='user.profile.profile_photo.url', allow_null=True)

    class Meta:
        model = Comment
        fields = ['user', 'full_name', 'profile_photo', 'content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    reaction = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    post_image = serializers.SerializerMethodField()
    user = UserProfileSerializer(read_only=True)
    user_reaction = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'caption', 'post_image', 'is_pinned',
            'reaction', 'user_reaction', 'is_bookmarked',
            'total_comments', 'created_at',
        ]

    def get_post_image(self, obj):
        if obj.post_image:
            return str(obj.post_image)
        return None

    def get_reaction(self, obj):
        return {
            'haha':  obj.reactions.filter(reaction_type='haha').count(),
            'love':  obj.reactions.filter(reaction_type='love').count(),
            'sad':   obj.reactions.filter(reaction_type='sad').count(),
            'angry': obj.reactions.filter(reaction_type='angry').count(),
        }

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        r = obj.reactions.filter(user=request.user).first()
        return r.reaction_type if r else None

    def get_is_bookmarked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=request.user).exists()

    def get_total_comments(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        user = self.context['request'].user
        post_image = self.context['request'].FILES.get('post_image')
        post = Post.objects.create(
            caption=validated_data.get('caption', ''),
            user=user
        )

        if post_image:
            try:
                cloudinary_response = cloudinary.uploader.upload(
                    post_image,
                    folder="Cintracon/post_images",
                    public_id=f"post_{post.id}" if hasattr(post, 'id') else None,
                    overwrite=True
                    )
                post.post_image = cloudinary_response.get('secure_url')
                post.save()
            except Exception as e:
                print(f"Error uploading image: {str(e)}")

        

        return post


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['report_type', 'reason']
    
    def create(self, validated_data):
        user = self.context['request'].user
        post = self.context.get('post')
        
        if not post:
            raise serializers.ValidationError("Post not found in context")
        
        # Check if user already reported this post
        if Report.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("You have already reported this post.")
        
        # Check if user is reporting their own post
        if post.user == user:
            raise serializers.ValidationError("You cannot report your own post.")
        
        report = Report.objects.create(
            user=user,
            post=post,
            **validated_data
        )
        return report
    
    def validate_report_type(self, value):
        # Report type validation
        valid_types = ['spam', 'harassment', 'misinformation', 'inappropriate_content', 'other']
        if value.lower() not in valid_types:
            raise serializers.ValidationError("Invalid report type")
        return value.lower()