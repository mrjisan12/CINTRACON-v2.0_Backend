
# home/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
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

            return api_response(True, "Post updated successfully", PostSerializer(post, context={'request': request}).data, code=200, status_code=200)

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

        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})

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
                "haha": post.reactions.filter(reaction_type="haha").count(),
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

        comment = Comment.objects.create(user=request.user, post=post, content=comment_content)

        # Notify post owner
        if post.user != request.user:
            try:
                from notifications.utils import create_notification
                create_notification(
                    recipient=post.user,
                    sender=request.user,
                    notif_type='comment',
                    message=f'{request.user.full_name} commented on your post.',
                    link=f'/home/post/{post.id}',
                )
            except Exception:
                pass

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
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return api_response(False, 'Post not found', None, 404, status.HTTP_404_NOT_FOUND)

        reaction_type = request.data.get('reaction_type')
        if reaction_type not in ['haha', 'love', 'wow', 'sad', 'angry']:
            return api_response(False, 'Invalid reaction type', None, 400, status.HTTP_400_BAD_REQUEST)

        existing = Reaction.objects.filter(user=request.user, post=post).first()
        user_reaction = None

        if existing:
            if existing.reaction_type == reaction_type:
                # Same type → toggle OFF
                existing.delete()
                user_reaction = None
            else:
                # Different type → switch
                existing.reaction_type = reaction_type
                existing.save(update_fields=['reaction_type'])
                user_reaction = reaction_type
        else:
            # No previous reaction → create
            Reaction.objects.create(user=request.user, post=post, reaction_type=reaction_type)
            user_reaction = reaction_type

            if post.user != request.user:
                try:
                    from notifications.utils import create_notification
                    create_notification(
                        recipient=post.user,
                        sender=request.user,
                        notif_type='like',
                        message=f'{request.user.full_name} reacted to your post.',
                        link=f'/home/post/{post.id}',
                    )
                except Exception:
                    pass

        reaction_counts = {
            'haha':  post.reactions.filter(reaction_type='haha').count(),
            'love':  post.reactions.filter(reaction_type='love').count(),
            'sad':   post.reactions.filter(reaction_type='sad').count(),
            'angry': post.reactions.filter(reaction_type='angry').count(),
        }
        return api_response(True, 'Reaction updated.', {
            'reaction': reaction_counts,
            'user_reaction': user_reaction,
        }, 200, status.HTTP_200_OK)



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
            
            
# Report Post View (To be implemented)
class ReportCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return api_response(False, "Post not found", code=404, status_code=404)
        
        # Context তৈরি করছি
        context = {
            'request': request,
            'post': post
        }
        
        serializer = ReportSerializer(data=request.data, context=context)
        
        if serializer.is_valid():
            try:
                report = serializer.save()
                return api_response(True, "Post reported successfully", data={
                    'id': report.id,
                    'report_type': report.report_type,
                    'reason': report.reason
                }, code=201)
            except serializers.ValidationError as e:
                # Better error message extraction
                if hasattr(e, 'detail'):
                    if isinstance(e.detail, list) and len(e.detail) > 0:
                        error_message = str(e.detail[0])
                    elif isinstance(e.detail, dict):
                        # যদি dictionary format এ error থাকে
                        first_error = list(e.detail.values())[0]
                        error_message = str(first_error[0]) if isinstance(first_error, list) else str(first_error)
                    else:
                        error_message = str(e.detail)
                else:
                    error_message = str(e)
                return api_response(False, error_message, code=400, status_code=400)
        
        # Serializer errors return করছি
        return api_response(False, "Invalid data", data=serializer.errors, code=400, status_code=400)


# ─── Bookmarks ────────────────────────────────────────────────────────────────

class BookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
            bm = Bookmark.objects.filter(user=request.user, post=post)
            if bm.exists():
                bm.delete()
                return api_response(True, 'Bookmark removed.', {'is_bookmarked': False}, 200, status.HTTP_200_OK)
            else:
                Bookmark.objects.create(user=request.user, post=post)
                return api_response(True, 'Post bookmarked.', {'is_bookmarked': True}, 200, status.HTTP_200_OK)
        except Post.DoesNotExist:
            return api_response(False, 'Post not found.', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyBookmarksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))

            bms = Bookmark.objects.filter(user=request.user).select_related('post')
            total = bms.count()
            start = (page - 1) * size
            posts = [bm.post for bm in bms[start:start + size]]
            return api_response(True, 'Bookmarks fetched.', PostSerializer(posts, many=True, context={'request': request}).data, 200, status.HTTP_200_OK,
                                pagination={'total': total, 'page': page, 'size': size,
                                            'total_pages': (total + size - 1) // size if size else 1})
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Global Search ────────────────────────────────────────────────────────────

class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from django.db.models import Q as DQ
            from users.models import CustomUser, UserProfile
            from notesharing.models import Note
            from jobopportunities.models import JobPost

            q = request.query_params.get('q', '').strip()
            search_type = request.query_params.get('type', 'all')
            limit = 5

            if not q:
                return api_response(False, 'Query parameter "q" is required.', None, 400, status.HTTP_400_BAD_REQUEST)

            result = {}

            if search_type in ('all', 'users'):
                profiles = UserProfile.objects.filter(
                    DQ(user__full_name__icontains=q) | DQ(user__email__icontains=q)
                ).select_related('user')[:limit]
                result['users'] = [
                    {
                        'id': p.user.id,
                        'name': p.user.full_name,
                        'profile_photo': p.profile_photo.url if p.profile_photo else None,
                        'department': p.department,
                        'semester': p.semester,
                        'batch_no': p.batch_no,
                    }
                    for p in profiles
                ]

            if search_type in ('all', 'posts'):
                posts = Post.objects.filter(caption__icontains=q).select_related('user')[:limit]
                result['posts'] = [
                    {
                        'id': p.id,
                        'content': p.caption[:120] if p.caption else '',
                        'author': p.user.full_name,
                        'created_at': p.created_at,
                    }
                    for p in posts
                ]

            if search_type in ('all', 'notes'):
                notes = Note.objects.filter(
                    DQ(title__icontains=q) | DQ(description__icontains=q)
                ).select_related('user')[:limit]
                result['notes'] = [
                    {
                        'id': n.id,
                        'title': n.title,
                        'department': n.department,
                        'uploaded_by': n.user.full_name,
                    }
                    for n in notes
                ]

            if search_type in ('all', 'jobs'):
                jobs = JobPost.objects.filter(
                    DQ(title__icontains=q) | DQ(company_name__icontains=q)
                )[:limit]
                result['jobs'] = [
                    {
                        'id': j.id,
                        'title': j.title,
                        'company_name': j.company_name,
                        'deadline': j.deadline,
                    }
                    for j in jobs
                ]

            return api_response(True, 'Search results.', result, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Public Detail (no auth required — for share links) ──────────────────────

class PublicPostDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        try:
            post = Post.objects.select_related('user__profile').prefetch_related(
                'comments__user__profile', 'reactions'
            ).get(id=post_id)

            profile = post.user.profile
            comments = [
                {
                    'id': c.id,
                    'content': c.content,
                    'created_at': c.created_at,
                    'user': {
                        'id': c.user.id,
                        'full_name': c.user.full_name,
                        'profile_photo': c.user.profile.profile_photo.url if c.user.profile.profile_photo else None,
                    },
                }
                for c in post.comments.select_related('user__profile').order_by('-created_at')
            ]
            data = {
                'id': post.id,
                'caption': post.caption,
                'post_image': str(post.post_image) if post.post_image else None,
                'created_at': post.created_at,
                'reaction_count': post.reactions.count(),
                'comment_count': post.comments.count(),
                'comments': comments,
                'user': {
                    'id': post.user.id,
                    'full_name': post.user.full_name,
                    'profile_photo': profile.profile_photo.url if profile.profile_photo else None,
                    'department': profile.department,
                },
            }
            return api_response(True, 'Post details fetched successfully!', data, 200, status.HTTP_200_OK)
        except Post.DoesNotExist:
            return api_response(False, 'Post not found', None, 404, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)