
# home/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser, UserProfile, UserPoints
from users.utils import api_response
from django.utils import timezone
from datetime import timedelta
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum

class PostPagination(PageNumberPagination):
    page_size = 10  # Adjust to the number of posts you want per request


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            # Manually pass the user from the request to the serializer's save method
            post = serializer.save()  # Associate the post with the logged-in user
            
            return Response(
                {
                    'msg': 'Post created successfully!', 
                    'success': True,
                    'data': PostSerializer(post).data,
                    'code': 200
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostEditView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return api_response(False, "Post not found", None, code=404, status_code=404)

        # Only owner can edit
        if post.user != request.user:
            return api_response(False, "You are not allowed to edit this post", None, code=403, status_code=403)

        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            # Handle image upload
            post_image = request.FILES.get('post_image')
            if post_image:
                try:
                    # Upload to Cloudinary in the same folder and overwrite existing
                    cloudinary_response = cloudinary.uploader.upload(
                        post_image,
                        folder="Cintracon/post_images",
                        public_id=f"post_{post.id}",  # ensures overwrite
                        overwrite=True
                    )
                    post.post_image = cloudinary_response.get('secure_url')
                except Exception as e:
                    return api_response(
                        False, f"Error uploading image: {str(e)}", None, code=500, status_code=500
                    )

            # Update caption if provided
            post.caption = serializer.validated_data.get('caption', post.caption)
            post.save()

            return api_response(True, "Post updated successfully", PostSerializer(post).data, code=200, status_code=200)

        return api_response(False, "Validation error", serializer.errors, code=400, status_code=400)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return api_response(False, "Post not found", None, code=404, status_code=404)

        # Only owner can delete
        if post.user != request.user:
            return api_response(False, "You are not allowed to delete this post", None, code=403, status_code=403)

        try:
            post.delete()
            return api_response(True, "Post deleted successfully", None, code=200, status_code=200)
        except Exception as e:
            return api_response(False, f"Error deleting post: {str(e)}", None, code=500, status_code=500)




class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get page and size from request body, default to 1 and 10
        page = int(request.data.get('page', 1))
        size = int(request.data.get('size', 10))

        posts = Post.objects.all().order_by('-created_at')
        total_posts = posts.count()
        start = (page - 1) * size
        end = start + size
        paginated_posts = posts[start:end]

        serializer = PostSerializer(paginated_posts, many=True)

        return Response({
            'msg': 'Posts retrieved successfully!',
            'success': True,
            'data': serializer.data,
            'code': 200
        }, status=status.HTTP_200_OK)
        
        
# Post Details API
class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        from users.utils import api_response
        try:
            post = Post.objects.select_related('user').get(id=post_id)
            # User info
            user_profile = post.user.profile
            user_info = {
                'full_name': post.user.full_name,
                'profile_photo': user_profile.profile_photo.url if user_profile.profile_photo else None
            }
            # Reactions
            reaction_counts = {
                "like": post.reactions.filter(reaction_type="like").count(),
                "love": post.reactions.filter(reaction_type="love").count(),
                "sad": post.reactions.filter(reaction_type="sad").count(),
                "angry": post.reactions.filter(reaction_type="angry").count(),
            }
            # Comments
            comments_qs = post.comments.all().order_by('-created_at')
            comments = [
                {
                    'user': c.user.id,
                    'full_name': c.user.full_name,
                    'profile_photo': c.user.profile.profile_photo.url if c.user.profile.profile_photo else None,
                    'content': c.content,
                    'created_at': c.created_at
                }
                for c in comments_qs
            ]
            data = {
                'id': post.id,
                'user': user_info,
                'caption': post.caption,
                'post_image': str(post.post_image) if post.post_image else None,
                'reaction': reaction_counts,
                'total_comments': post.comments.count(),
                'comments': comments,
                'created_at': post.created_at
            }
            return api_response(True, 'Post details fetched successfully!', data, 200, status.HTTP_200_OK)
        except Post.DoesNotExist:
            return api_response(False, 'Post not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# For Create Comment API        
class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, post_id):
        # Get the post object the user is commenting on
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"msg": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the comment content from the request data
        comment_content = request.data.get('content', None)
        if not comment_content:
            return Response({"msg": "Comment content cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new comment
        comment = Comment.objects.create(
            user=request.user,  # Associate the logged-in user
            post=post,           # Associate the post with the comment
            content=comment_content  # The content of the comment
        )

        # Return the serialized comment data
        serializer = CommentSerializer(comment)
        return Response({
            "msg": "Comment created successfully",
            "success": True,
            "data": serializer.data,
            "code": 201
        }, status=status.HTTP_201_CREATED)
        
        
        
        
# For Giving Reaction 
class ReactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        # Get the post the user is reacting to
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"msg": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the reaction type from the request data
        reaction_type = request.data.get('reaction_type', None)
        if reaction_type not in ['like', 'love', 'wow', 'sad', 'angry']:
            return Response({"msg": "Invalid reaction type"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has already reacted with the same reaction type
        existing_reaction = Reaction.objects.filter(user=request.user, post=post)

        if existing_reaction.exists():
            current_reaction = existing_reaction.first()
            # If the reaction type is the same, do nothing
            if current_reaction.reaction_type == reaction_type:
                return Response({"msg": "You already reacted with this type"}, status=status.HTTP_200_OK)
            # Otherwise, update the reaction
            existing_reaction.update(reaction_type=reaction_type)
            return Response({"msg": "Reaction updated successfully"}, status=status.HTTP_200_OK)
        else:
            # If the user has not reacted yet, create a new reaction
            Reaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)
            return Response({"msg": "Reaction added successfully"}, status=status.HTTP_201_CREATED)



# Specific Post All Comments
class PostAllCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({
                "msg": "Post not found",
                "success": False,
                "code": 404
            }, status=status.HTTP_404_NOT_FOUND)

        comments = post.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)

        return Response({
            "msg": "All comments retrieved successfully",
            "success": True,
            "data": {
                "comments": serializer.data
            },
            "code": 200
        }, status=status.HTTP_200_OK)
        
        
# Right Sidebar Info
class RightSidebarInfoView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            # Get user info
            user_profile = UserProfile.objects.get(user=user)
            # user_info = {
            #     'full_name': user.full_name,
            #     'profile_photo': user_profile.profile_photo.url if user_profile.profile_photo else None,
            #     'department': user_profile.department,
            #     'semester': user_profile.semester,
            # }

            # Get top 10 users by points in last 7 days
            seven_days_ago = timezone.now() - timedelta(days=7)
            # Aggregate points for each user in last 7 days
            points_qs = UserPoints.objects.filter(created_at__gte=seven_days_ago)
            leaderboard = (
                points_qs.values('user')
                .annotate(total_points=Sum('points'))
                .order_by('-total_points')[:10]
            )
            # Get user info for leaderboard
            user_ids = [entry['user'] for entry in leaderboard]
            users = CustomUser.objects.filter(id__in=user_ids)
            profiles = UserProfile.objects.filter(user_id__in=user_ids)
            user_map = {u.id: u for u in users}
            profile_map = {p.user_id: p for p in profiles}
            leaderboard_data = []
            for entry in leaderboard:
                uid = entry['user']
                u = user_map.get(uid)
                p = profile_map.get(uid)
                leaderboard_data.append({
                    'id': u.id,
                    'full_name': u.full_name if u else None,
                    'profile_photo': p.profile_photo.url if p and p.profile_photo else None,
                    'department': p.department if p else None,
                    'semester': p.semester if p else None,
                    'total_points': entry['total_points']
                })

            data = {
                # 'user_info': user_info,
                'top_users': leaderboard_data
            }
            return api_response(True, 'Sidebar info fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# Nav Bar Info
class NavBarInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            data = {
                'full_name': user.full_name,
                'profile_photo': user_profile.profile_photo.url if user_profile.profile_photo else None,
                'points': user_profile.points
            }
            from users.utils import api_response
            return api_response(True, 'Nav bar info fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            from users.utils import api_response
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        
        
class DeveloperListView(APIView):
    permission_classes = [IsAuthenticated]  # শুধু authenticated users

    def get(self, request):
        try:
            # শুধু developer users গুলো fetch করুন
            developers = UserProfile.objects.filter(
                is_developer=True
            ).select_related('user').order_by('user__id')  # Optimize query

            developers_data = []
            for profile in developers:
                developers_data.append({
                    'id': profile.user.id,
                    'full_name': profile.user.full_name,
                    'profile_photo': profile.profile_photo.url if profile.profile_photo else None,
                    'department': profile.department,
                    'semester': profile.semester,
                    # প্রয়োজন হলে আরও fields যোগ করুন
                })

            return api_response(
                True, 
                'Developers list fetched successfully!', 
                developers_data, 
                200, 
                status.HTTP_200_OK
            )

        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )