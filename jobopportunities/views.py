from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import JobPostSerializer
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework.pagination import PageNumberPagination
from .utils import api_response


class JobPostPagination(PageNumberPagination):
    page_size = 10  # Adjust to the number of posts you want per request


class JobPostCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can create job posts

    def post(self, request):
        # Add the user from the request to the data before saving
        serializer = JobPostSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user explicitly
            return api_response(
                True, 
                'Job post successfully created!', 
                serializer.data, 
                201, 
                status.HTTP_201_CREATED
            )
        
        return api_response(
            False, 
            'Validation error', 
            serializer.errors, 
            400, 
            status.HTTP_400_BAD_REQUEST
        )


class JobPostListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            
            # Validate page and size
            if page < 1:
                return api_response(False, 'Page must be greater than 0', None, 400, status.HTTP_400_BAD_REQUEST)
            if size < 1:
                return api_response(False, 'Size must be greater than 0', None, 400, status.HTTP_400_BAD_REQUEST)
            
            job_posts = JobPost.objects.all().order_by('-created_at')
            total = job_posts.count()
            start = (page - 1) * size
            end = start + size
            
            # Check if page exists
            if start >= total:
                return api_response(True, 'No more job posts available', [], 200, status.HTTP_200_OK)
            
            paginated = job_posts[start:end]
            serializer = JobPostSerializer(paginated, many=True)
            
            # Return response with pagination info
            data = serializer.data
            
            return api_response(True, 'Job posts fetched successfully!', data, 200, status.HTTP_200_OK)
            
        except ValueError:
            return api_response(False, 'Invalid page or size parameter', None, 400, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    
    
class JobPostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        try:
            # Get the job post
            job_post = JobPost.objects.get(id=job_id)
            
            # Check if the logged-in user is the owner of the job post
            if job_post.user != request.user:
                return api_response(
                    False, 
                    'You can only delete your own job posts', 
                    None, 
                    403, 
                    status.HTTP_403_FORBIDDEN
                )
            
            # Delete the job post
            job_post.delete()
            
            return api_response(
                True, 
                'Job post deleted successfully!', 
                None, 
                200, 
                status.HTTP_200_OK
            )
            
        except JobPost.DoesNotExist:
            return api_response(
                False, 
                'Job post not found', 
                None, 
                404, 
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return api_response(
                False, 
                f'Server error: {str(e)}', 
                None, 
                500, 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )