from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

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


# class PostListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Get all posts along with their reactions and comments
#         posts = Post.objects.all()
        
#         # Serialize the posts
#         serializer = PostSerializer(posts, many=True)
#         pagination_class = PostPagination
        
#         return Response(
#             {
#                 'msg': 'Posts retrieved successfully!',
#                 'success': True,
#                 'data': serializer.data,
#                 'code': 200
#             }, status=status.HTTP_200_OK)
        
        
class PostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all posts along with their reactions and comments
        posts = Post.objects.all()
        
        # Paginate the queryset
        paginator = PostPagination()
        result_page = paginator.paginate_queryset(posts, request)
        
        # Serialize the paginated posts
        serializer = PostSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(
            {
                'msg': 'Posts retrieved successfully!',
                'success': True,
                'data': serializer.data,
                'code': 200
            }
        )

        
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