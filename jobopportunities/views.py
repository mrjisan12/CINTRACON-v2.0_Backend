from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import JobPostSerializer
from rest_framework.permissions import IsAuthenticated
from .models import *
from rest_framework.pagination import PageNumberPagination


class JobPostPagination(PageNumberPagination):
    page_size = 10  # Adjust to the number of posts you want per request



class JobPostCreateView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can create job posts

    def post(self, request):
        # Add the user from the request to the data before saving
        serializer = JobPostSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(user=request.user)  # Set the user explicitly
            return Response({
                'msg': 'Job post successfully created!',
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class JobPostListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .utils import api_response
        try:
            page = int(request.data.get('page', 1))
            size = int(request.data.get('size', 10))
            job_posts = JobPost.objects.all().order_by('-created_at')
            total = job_posts.count()
            start = (page - 1) * size
            end = start + size
            paginated = job_posts[start:end]
            serializer = JobPostSerializer(paginated, many=True)
            data = {
                'results': serializer.data,
                'total': total,
                'page': page,
                'size': size
            }
            return api_response(True, 'Job posts fetched successfully!', data, 200, status.HTTP_200_OK)
        except Exception as e:
            return api_response(False, f'Server error: {str(e)}', None, 500, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
