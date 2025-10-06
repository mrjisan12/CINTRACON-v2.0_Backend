# serializers.py
import cloudinary.uploader
from rest_framework import serializers
from .models import Post, Reaction, Comment
#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    profile_photo = serializers.CharField(source='profile.profile_photo.url', allow_null=True)

    class Meta:
        model = User
        fields = ['full_name', 'profile_photo']



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
    # comments = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    post_image = serializers.SerializerMethodField()
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'post_image', 'reaction', 'total_comments', 'created_at']

    def get_post_image(self, obj):
        if obj.post_image:
            return str(obj.post_image)
        return None

    def get_reaction(self, obj):
        reaction_counts = {
            "like": obj.reactions.filter(reaction_type="like").count(),
            "love": obj.reactions.filter(reaction_type="love").count(),
            "sad": obj.reactions.filter(reaction_type="sad").count(),
            "angry": obj.reactions.filter(reaction_type="angry").count(),
        }
        return reaction_counts

    # def get_comments(self, obj):
    #     comments = obj.comments.all().order_by('-created_at')[:2]
    #     return CommentSerializer(comments, many=True).data

    def get_total_comments(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        user = self.context['request'].user
        post_image = self.context['request'].FILES.get('post_image')
        post_image_url = None

        if post_image:
            try:
                cloudinary_response = cloudinary.uploader.upload(post_image)
                post_image_url = cloudinary_response.get('secure_url')
            except Exception as e:
                print(f"Error uploading image: {str(e)}")

        post = Post.objects.create(
            caption=validated_data.get('caption', ''),
            post_image=post_image_url,
            user=user
        )

        return post


# Trying to add field post_detail in NewsFeed API

# class PostSerializer(serializers.ModelSerializer):
#     reaction = serializers.SerializerMethodField()
#     comments = serializers.SerializerMethodField()
#     total_comments = serializers.SerializerMethodField()
#     post_image = serializers.SerializerMethodField()
#     user = UserProfileSerializer()  # Add user information
#     post_detail = serializers.SerializerMethodField()  # Add post_detail field

#     class Meta:
#         model = Post
#         fields = ['id', 'user', 'post_detail','post_image', 'reaction', 'comments', 'total_comments']  # Ensure all fields are included

#     def get_post_image(self, obj):
#         if obj.post_image:
#             return str(obj.post_image)
#         return None

#     def get_reaction(self, obj):
#         # Count reactions for each type
#         reaction_counts = {
#             "like": obj.reactions.filter(reaction_type="like").count(),
#             "love": obj.reactions.filter(reaction_type="love").count(),
#             "sad": obj.reactions.filter(reaction_type="sad").count(),
#             "angry": obj.reactions.filter(reaction_type="angry").count(),
#         }
#         return reaction_counts

#     def get_comments(self, obj):
#         # Get all comments for the post and serialize them
#         comments = obj.comments.all().order_by('-created_at')  # Get comments in descending order
#         return CommentSerializer(comments, many=True).data

#     def get_total_comments(self, obj):
#         # Get total number of comments
#         return obj.comments.count()

#     def get_post_detail(self, obj):
#         # This method combines all relevant data into the post_detail field
#         return {
#             'caption': obj.caption,
#             'post_image': self.get_post_image(obj),
#             'reaction': self.get_reaction(obj),
#             'comments': self.get_comments(obj),
#             'total_comments': self.get_total_comments(obj),
#             'created_at': obj.created_at,
#         }

#     def create(self, validated_data):
#         post_image = validated_data.get('post_image', None)
#         post_image_url = None

#         # If post_image is provided, upload to Cloudinary and get the correct URL
#         if post_image:
#             cloudinary_response = cloudinary.uploader.upload(post_image)
#             post_image_url = cloudinary_response.get('secure_url')  # Get the full Cloudinary URL

#         # Create the post and assign the user as well
#         post = Post.objects.create(
#             caption=validated_data['caption'],
#             post_image=post_image_url if post_image else None,  # Store the correct Cloudinary URL
#             user=validated_data.get('user'),  # Assign the user to the post
#         )

#         return post